import os
import yaml
import docker
import logging
import random

# Set up logging
logging.basicConfig(filename='docker_helper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_client(docker_host=None):
    """
    Get a Docker client, either local or remote via SSH.

    Args:
        docker_host: Optional Docker host connection string. Supports:
            - None: Connect to local Docker daemon (default)
            - "ssh://user@host": Connect via SSH (uses SSH keys)
            - "ssh://user@host:port": Connect via SSH with custom port
            - "unix:///var/run/docker.sock": Local socket (explicit)
            - "tcp://host:port": TCP connection

    Returns:
        Docker client instance

    Raises:
        ConnectionError: If connection fails
    """
    try:
        if docker_host:
            # Connect to remote or specific host
            logging.info(f"Connecting to Docker host: {docker_host}")
            client = docker.DockerClient(base_url=docker_host)
            # Test connection
            client.ping()
            logging.info(f"Successfully connected to Docker host: {docker_host}")

            # Verify connection by getting server info
            info = client.info()
            logging.info(f"Connected to Docker daemon. Server name: {info.get('Name', 'Unknown')}")
        else:
            # Connect to local Docker daemon
            client = docker.from_env()
            logging.info("Connected to local Docker daemon")

            # Verify connection
            info = client.info()
            logging.info(f"Connected to local Docker daemon. Server name: {info.get('Name', 'Unknown')}")

        return client
    except docker.errors.DockerException as e:
        logging.error(f"Error connecting to Docker: {e}")
        if docker_host:
            raise ConnectionError(f"Error connecting to Docker at {docker_host}. Please check the connection and ensure Docker is running.")
        else:
            raise ConnectionError("Error connecting to Docker. Please make sure Docker is running.")

def handle_configure(token, domain):
    with open('duckdns.yml', 'w') as f:
        yaml.dump({'duckdns': {'token': token, 'domain': domain}}, f)
    return "DuckDNS settings updated."

# Determine the services directory path
def get_services_directory():
    """
    Get the path to the services directory.

    Searches in the following order:
    1. /opt/docker-helper/services (system installation)
    2. ./services (development/local installation)
    3. <script_dir>/services (relative to this file)

    Returns:
        str: Path to the services directory

    Raises:
        FileNotFoundError: If services directory cannot be found
    """
    # Try system installation path first
    if os.path.exists('/opt/docker-helper/services'):
        return '/opt/docker-helper/services'

    # Try current directory
    if os.path.exists('services'):
        return 'services'

    # Try relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    services_dir = os.path.join(script_dir, 'services')
    if os.path.exists(services_dir):
        return services_dir

    raise FileNotFoundError("Services directory not found. Please ensure docker-helper is installed correctly.")

def load_service_config(service_name):
    """
    Load a service configuration from a YAML file.

    Args:
        service_name: Name of the service (without .yml extension)

    Returns:
        dict: Service configuration

    Raises:
        FileNotFoundError: If service configuration file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    services_dir = get_services_directory()
    service_file = os.path.join(services_dir, f"{service_name}.yml")

    if not os.path.exists(service_file):
        raise FileNotFoundError(f"Service configuration not found: {service_name}")

    with open(service_file, 'r') as f:
        service_config = yaml.safe_load(f)

    logging.info(f"Loaded service configuration: {service_name}")
    return service_config

def get_available_services():
    """
    Get a list of all available service configurations.

    Returns:
        list: List of service configuration dictionaries
    """
    services = []
    try:
        services_dir = get_services_directory()
    except FileNotFoundError:
        logging.warning("Services directory not found")
        return services

    for filename in os.listdir(services_dir):
        if filename.endswith('.yml'):
            try:
                with open(os.path.join(services_dir, filename), 'r') as f:
                    services.append(yaml.safe_load(f))
            except yaml.YAMLError as e:
                logging.error(f"Error parsing service definition file {filename}: {e}")
    return services

def get_installed_services(client):
    return [container.name for container in client.containers.list(all=True)]

def install_service(client, service_config, config_values):
    """
    Install (create and start) a Docker container from a service configuration.

    Args:
        client: Docker client instance
        service_config: Service definition dictionary from YAML
        config_values: User-provided configuration values

    Returns:
        str: Success message with container ID

    Raises:
        ValueError: If service configuration is invalid
        docker.errors.DockerException: If Docker operation fails
    """
    try:
        # Validate service configuration
        if 'name' not in service_config:
            raise ValueError("Service configuration missing 'name' field")
        if 'image' not in service_config:
            raise ValueError("Service configuration missing 'image' field")

        service_name = service_config['name']
        image = service_config['image']

        # Validate and get container name
        container_name = config_values.get('container_name')
        if not container_name:
            container_name = service_name

        # Validate container name (Docker naming rules)
        import re
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$', container_name):
            raise ValueError(f"Invalid container name: {container_name}. Must match [a-zA-Z0-9][a-zA-Z0-9_.-]*")

        logging.info(f"Installing service '{service_name}' as container '{container_name}'")

        # Build environment variables
        environment = {}
        volumes = {}

        # Process variables
        for var in service_config.get('variables', []):
            var_name = var['name']
            user_value = config_values.get('variables', {}).get(var_name)

            if user_value is None:
                continue

            var_type = var.get('type', 'string')

            # Check if this is a path/directory with volume mapping enabled
            if var_type in ['path', 'directory']:
                volume_mappings = config_values.get('volume_mappings', {})
                if var_name in volume_mappings and volume_mappings[var_name].get('enabled'):
                    # Use volume mapping
                    host_path = volume_mappings[var_name].get('host_path')
                    container_path = volume_mappings[var_name].get('container_path')
                    if host_path and container_path:
                        volumes[host_path] = {'bind': container_path, 'mode': 'rw'}
                        logging.info(f"Volume mapping: {host_path} -> {container_path}")
                else:
                    # Set as environment variable if no volume mapping
                    environment[var_name] = str(user_value)
            else:
                # Regular environment variable
                environment[var_name] = str(user_value)

        # Build port mappings
        ports = {}
        for port in service_config.get('ports', []):
            port_name = port['name']
            host_port = config_values.get('ports', {}).get(port_name)
            if host_port is not None:
                container_port = port['container']
                protocol = port.get('protocol', 'tcp')
                port_key = f"{container_port}/{protocol}"
                ports[port_key] = host_port
                logging.info(f"Port mapping: {host_port} -> {container_port}/{protocol}")

        # Pull image if not present
        logging.info(f"Pulling image: {image}")
        try:
            client.images.pull(image)
        except docker.errors.ImageNotFound:
            raise ValueError(f"Image not found: {image}")
        except Exception as e:
            logging.warning(f"Failed to pull image {image}: {e}. Will try to use local image.")

        # Create and start container
        logging.info(f"Creating container '{container_name}' from image '{image}'")
        container = client.containers.run(
            image=image,
            name=container_name,
            environment=environment,
            ports=ports,
            volumes=volumes,
            detach=True,
            restart_policy={"Name": "unless-stopped"}
        )

        logging.info(f"Container '{container_name}' created successfully with ID: {container.short_id}")
        return f"✓ Service '{service_name}' installed successfully as container '{container_name}' (ID: {container.short_id})"

    except docker.errors.ContainerError as e:
        error_msg = f"Container failed to start: {e}"
        logging.error(error_msg)
        raise docker.errors.DockerException(error_msg)
    except docker.errors.ImageNotFound as e:
        error_msg = f"Image not found: {image}"
        logging.error(error_msg)
        raise docker.errors.DockerException(error_msg)
    except docker.errors.APIError as e:
        error_msg = f"Docker API error: {e}"
        logging.error(error_msg)
        raise docker.errors.DockerException(error_msg)
    except Exception as e:
        logging.error(f"Error installing service '{service_config.get('name')}': {e}")
        raise

def uninstall_service(client, service_name):
    """
    Uninstall (stop and remove) a Docker container.

    Args:
        client: Docker client instance
        service_name: Name of the container to remove

    Returns:
        str: Success message

    Raises:
        docker.errors.NotFound: If container doesn't exist
        docker.errors.APIError: If Docker operation fails
    """
    try:
        logging.info(f"Uninstalling service: {service_name}")

        # Get container
        container = client.containers.get(service_name)

        # Stop container if running
        if container.status == 'running':
            logging.info(f"Stopping container '{service_name}'")
            container.stop(timeout=10)

        # Remove container
        logging.info(f"Removing container '{service_name}'")
        container.remove()

        logging.info(f"Container '{service_name}' uninstalled successfully")
        return f"✓ Service '{service_name}' uninstalled successfully"

    except docker.errors.NotFound:
        error_msg = f"Container '{service_name}' not found"
        logging.error(error_msg)
        raise docker.errors.NotFound(error_msg)
    except docker.errors.APIError as e:
        error_msg = f"Failed to uninstall '{service_name}': {e}"
        logging.error(error_msg)
        raise docker.errors.APIError(error_msg)

def start_service(client, service_name):
    """
    Start a stopped Docker container.

    Args:
        client: Docker client instance
        service_name: Name of the container to start

    Returns:
        str: Success message

    Raises:
        docker.errors.NotFound: If container doesn't exist
        docker.errors.APIError: If Docker operation fails
    """
    try:
        logging.info(f"Starting service: {service_name}")

        # Get container
        container = client.containers.get(service_name)

        # Check if already running
        if container.status == 'running':
            return f"Service '{service_name}' is already running"

        # Start container
        container.start()

        logging.info(f"Container '{service_name}' started successfully")
        return f"✓ Service '{service_name}' started successfully"

    except docker.errors.NotFound:
        error_msg = f"Container '{service_name}' not found"
        logging.error(error_msg)
        raise docker.errors.NotFound(error_msg)
    except docker.errors.APIError as e:
        error_msg = f"Failed to start '{service_name}': {e}"
        logging.error(error_msg)
        raise docker.errors.APIError(error_msg)

def stop_service(client, service_name):
    """
    Stop a running Docker container.

    Args:
        client: Docker client instance
        service_name: Name of the container to stop

    Returns:
        str: Success message

    Raises:
        docker.errors.NotFound: If container doesn't exist
        docker.errors.APIError: If Docker operation fails
    """
    try:
        logging.info(f"Stopping service: {service_name}")

        # Get container
        container = client.containers.get(service_name)

        # Check if already stopped
        if container.status != 'running':
            return f"Service '{service_name}' is not running"

        # Stop container with 10 second timeout
        container.stop(timeout=10)

        logging.info(f"Container '{service_name}' stopped successfully")
        return f"✓ Service '{service_name}' stopped successfully"

    except docker.errors.NotFound:
        error_msg = f"Container '{service_name}' not found"
        logging.error(error_msg)
        raise docker.errors.NotFound(error_msg)
    except docker.errors.APIError as e:
        error_msg = f"Failed to stop '{service_name}': {e}"
        logging.error(error_msg)
        raise docker.errors.APIError(error_msg)

def restart_service(client, service_name):
    """
    Restart a Docker container.

    Args:
        client: Docker client instance
        service_name: Name of the container to restart

    Returns:
        str: Success message

    Raises:
        docker.errors.NotFound: If container doesn't exist
        docker.errors.APIError: If Docker operation fails
    """
    try:
        logging.info(f"Restarting service: {service_name}")

        # Get container
        container = client.containers.get(service_name)

        # Restart container with 10 second timeout
        container.restart(timeout=10)

        logging.info(f"Container '{service_name}' restarted successfully")
        return f"✓ Service '{service_name}' restarted successfully"

    except docker.errors.NotFound:
        error_msg = f"Container '{service_name}' not found"
        logging.error(error_msg)
        raise docker.errors.NotFound(error_msg)
    except docker.errors.APIError as e:
        error_msg = f"Failed to restart '{service_name}': {e}"
        logging.error(error_msg)
        raise docker.errors.APIError(error_msg)

def get_status(client, services):
    statuses = []
    if not services:
        services = [container.name for container in client.containers.list(all=True)]

    for service_name in services:
        try:
            container = client.containers.get(service_name)
            statuses.append(f"- {service_name}: {container.status}")
        except docker.errors.NotFound:
            statuses.append(f"- {service_name}: not installed")
    return "\n".join(statuses)

def get_running_container_details(client):
    from datetime import datetime, timezone
    details = []
    running_containers = client.containers.list(filters={'status': 'running'})
    for container in running_containers:
        name = container.name
        short_id = container.short_id

        # Get status
        status = container.status

        # Get image name (strip tag for cleaner display)
        image = container.image.tags[0] if container.image.tags else container.image.short_id

        # Calculate uptime
        try:
            start_time_str = container.attrs['State']['StartedAt']
            start_time = datetime.fromisoformat(start_time_str.split('.')[0] + 'Z').replace(tzinfo=timezone.utc)
            uptime_delta = datetime.now(timezone.utc) - start_time

            # Format uptime nicely
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            if days > 0:
                uptime = f"{days}d {hours}h"
            elif hours > 0:
                uptime = f"{hours}h {minutes}m"
            else:
                uptime = f"{minutes}m"
        except Exception:
            uptime = "N/A"

        # Get ports
        ports = container.ports
        port_mapping = []
        for container_port, host_ports in ports.items():
            if host_ports:
                host_port_num = host_ports[0]['HostPort']
                container_port_num = container_port.split('/')[0]
                port_mapping.append(f"{host_port_num}:{container_port_num}")

        networks = container.attrs['NetworkSettings']['Networks']
        network_names = ", ".join(networks.keys())

        details.append({
            "id": short_id,
            "name": name,
            "status": status,
            "image": image,
            "uptime": uptime,
            "ports": "\n".join(port_mapping) or "N/A",
            "network": network_names or "N/A"
        })
    return details

def get_full_container_details(client, container_id):
    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        return "Container not found."

    attrs = container.attrs
    
    # Uptime
    try:
        from datetime import datetime, timezone
        start_time_str = attrs['State']['StartedAt']
        start_time = datetime.fromisoformat(start_time_str.split('.')[0] + 'Z').replace(tzinfo=timezone.utc)
        uptime = datetime.now(timezone.utc) - start_time
        uptime_str = str(uptime).split('.')[0]
    except Exception:
        uptime_str = "N/A"

    # Volumes
    mounts = attrs.get('Mounts', [])
    volumes_str = "\n".join([f"- {m['Source']}:{m['Destination']}" for m in mounts]) or "None"

    # Env Vars
    env_vars = attrs['Config'].get('Env', [])
    env_vars_str = "\n".join([f"- {e}" for e in env_vars]) or "None"

    # Network
    networks = attrs.get('NetworkSettings', {}).get('Networks', {})
    network_details = []
    for name, data in networks.items():
        ip = data.get('IPAddress', 'N/A')
        mac = data.get('MacAddress', 'N/A')
        network_details.append(f"- {name}:\n  IP: {ip}\n  MAC: {mac}")
    network_str = "\n".join(network_details) or "None"

    report = f"""
<b>ID:</b> {container.short_id}
<b>Name:</b> {container.name}
<b>Image:</b> {attrs['Config']['Image']}
<b>Status:</b> {attrs['State']['Status']}
<b>Uptime:</b> {uptime_str}

<b>Volumes:</b>
{volumes_str}

<b>Environment Variables:</b>
{env_vars_str}

<b>Network Settings:</b>
{network_str}
    """
    return report


def update_service(client, service_name):
    """
    Update a Docker container to the latest image version.

    This recreates the container with the same configuration but latest image.

    Args:
        client: Docker client instance
        service_name: Name of the container to update

    Returns:
        str: Success message

    Raises:
        docker.errors.NotFound: If container doesn't exist
        docker.errors.APIError: If Docker operation fails
    """
    try:
        logging.info(f"Updating service: {service_name}")

        # Get existing container
        old_container = client.containers.get(service_name)

        # Get container configuration
        config = old_container.attrs['Config']
        host_config = old_container.attrs['HostConfig']

        # Extract important settings
        image = config['Image']
        environment = config.get('Env', [])
        volumes = host_config.get('Binds', [])
        port_bindings = host_config.get('PortBindings', {})
        restart_policy = host_config.get('RestartPolicy', {})

        logging.info(f"Pulling latest image: {image}")

        # Pull latest image
        try:
            client.images.pull(image)
        except Exception as e:
            logging.warning(f"Failed to pull image {image}: {e}")
            return f"⚠ Failed to pull latest image for '{service_name}': {e}"

        # Stop and remove old container
        logging.info(f"Stopping old container '{service_name}'")
        if old_container.status == 'running':
            old_container.stop(timeout=10)

        logging.info(f"Removing old container '{service_name}'")
        old_container.remove()

        # Parse volumes for new container
        volume_dict = {}
        if volumes:
            for volume in volumes:
                parts = volume.split(':')
                if len(parts) >= 2:
                    volume_dict[parts[0]] = {'bind': parts[1], 'mode': 'rw'}

        # Parse port bindings
        ports_dict = {}
        if port_bindings:
            for container_port, host_info in port_bindings.items():
                if host_info:
                    ports_dict[container_port] = host_info[0]['HostPort']

        # Create new container with same configuration
        logging.info(f"Creating updated container '{service_name}'")
        new_container = client.containers.run(
            image=image,
            name=service_name,
            environment=environment,
            volumes=volume_dict,
            ports=ports_dict,
            detach=True,
            restart_policy=restart_policy
        )

        logging.info(f"Container '{service_name}' updated successfully with ID: {new_container.short_id}")
        return f"✓ Service '{service_name}' updated successfully (new ID: {new_container.short_id})"

    except docker.errors.NotFound:
        error_msg = f"Container '{service_name}' not found"
        logging.error(error_msg)
        raise docker.errors.NotFound(error_msg)
    except docker.errors.APIError as e:
        error_msg = f"Failed to update '{service_name}': {e}"
        logging.error(error_msg)
        raise docker.errors.APIError(error_msg)
    except Exception as e:
        error_msg = f"Error updating service '{service_name}': {e}"
        logging.error(error_msg)
        raise

def test_container(client):
    logging.info("Starting test container...")
    port = random.randint(10000, 20000)
    try:
        container = client.containers.run(
            'alpine',
            name='temp_test_container',
            ports={'80/tcp': port},
            detach=True
        )
        logging.info(f"Test container started on port {port}")
        result = f"Test container started on port {port}"
        container.stop()
        container.remove()
        logging.info("Test container stopped and removed.")
        return result + "\nTest container stopped and removed."
    except Exception as e:
        logging.error(f"Error starting or stopping test container: {e}")
        return f"Error starting or stopping test container: {e}"
