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

def get_available_services():
    services = []
    if not os.path.exists('services'):
        return services
    for filename in os.listdir('services'):
        if filename.endswith('.yml'):
            try:
                with open(f'services/{filename}', 'r') as f:
                    services.append(yaml.safe_load(f))
            except yaml.YAMLError as e:
                logging.error(f"Error parsing service definition file {filename}: {e}")
    return services

def get_installed_services(client):
    return [container.name for container in client.containers.list(all=True)]

def install_service(service_config, config_values):
    try:
        command = ["docker", "run", "-d"]

        # Use custom container name if provided, otherwise use service name
        container_name = config_values.get('container_name')
        if not container_name:
            container_name = service_config.get('name', 'default-service-name')

        command.extend(["--name", container_name])

        # Process variables (environment and volumes)
        for var in service_config.get('variables', []):
            var_name = var['name']
            user_value = config_values['variables'].get(var_name)

            if user_value is None:
                continue

            var_type = var.get('type', 'string')

            # Check if this is a path/directory with volume mapping enabled
            if var_type in ['path', 'directory']:
                # Check if volume mapping is enabled for this variable
                volume_mappings = config_values.get('volume_mappings', {})
                if var_name in volume_mappings and volume_mappings[var_name]['enabled']:
                    # Use volume mapping
                    host_path = volume_mappings[var_name]['host_path']
                    container_path = volume_mappings[var_name]['container_path']
                    if host_path and container_path:
                        command.extend(["-v", f"{host_path}:{container_path}"])
                else:
                    # Set as environment variable if no volume mapping
                    command.extend(["-e", f"{var_name}={user_value}"])
            elif var_type == 'path':
                # Old behavior for backward compatibility
                container_path = var.get('default', '') # The YAML default is the container path
                command.extend(["-v", f"{user_value}:{container_path}"])
            else:
                command.extend(["-e", f"{var_name}={user_value}"])

        # Process ports
        for port in service_config.get('ports', []):
            port_name = port['name']
            host_port = config_values['ports'].get(port_name)
            if host_port is not None:
                container_port = port['container']
                protocol = port.get('protocol', 'tcp')
                command.extend(["-p", f"{host_port}:{container_port}/{protocol}"])

        # Add image name at the end
        image = service_config.get('image')
        if not image:
            return "Error: Image name not found in service configuration."
        command.append(image)

        # For now, just return the command as a string
        return "Generated command:\n" + " ".join(command)

    except Exception as e:
        logging.error(f"Error generating install command for {service_config.get('name')}: {e}")
        return f"Error generating command: {e}"

def uninstall_service(client, service_name):
    logging.info(f"Uninstalling service: {service_name}")
    # This is a test run, so we will not actually uninstall the service
    return f"Service {service_name} would be uninstalled."

def start_service(client, service_name):
    logging.info(f"Starting service: {service_name}")
    # This is a test run, so we will not actually start the service
    return f"Service {service_name} would be started."

def stop_service(client, service_name):
    logging.info(f"Stopping service: {service_name}")
    # This is a test run, so we will not actually stop the service
    return f"Service {service_name} would be stopped."

def restart_service(client, service_name):
    logging.info(f"Restarting service: {service_name}")
    # This is a test run, so we will not actually restart the service
    return f"Service {service_name} would be restarted."

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
    logging.info(f"Updating service: {service_name}")
    # This is a test run, so we will not actually update the service
    return f"Service {service_name} would be updated."

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
