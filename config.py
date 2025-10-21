"""
Configuration management for docker_helper
Handles remote Docker host configurations
"""

import os
import yaml
import logging

CONFIG_FILE = os.path.expanduser('~/.config/docker_helper/config.yml')

def ensure_config_dir():
    """Ensure the configuration directory exists."""
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

def load_config():
    """
    Load configuration from file.

    Returns:
        dict: Configuration dictionary or empty dict if file doesn't exist
    """
    if not os.path.exists(CONFIG_FILE):
        return {}

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f) or {}
            logging.info(f"Loaded configuration from {CONFIG_FILE}")
            return config
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        return {}

def save_config(config):
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary to save
    """
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        logging.info(f"Saved configuration to {CONFIG_FILE}")
    except Exception as e:
        logging.error(f"Error saving config file: {e}")
        raise

def get_docker_host():
    """
    Get the Docker host from configuration.

    Returns:
        str or None: Docker host connection string or None for local
    """
    config = load_config()
    return config.get('docker_host')

def set_docker_host(docker_host):
    """
    Set the Docker host in configuration.

    Args:
        docker_host: Docker host connection string (or None/empty for local)
    """
    config = load_config()
    if docker_host:
        config['docker_host'] = docker_host
    elif 'docker_host' in config:
        del config['docker_host']
    save_config(config)

def add_remote_host(name, host, port=22, user=None, description=None):
    """
    Add a named remote host configuration.

    Args:
        name: Name/alias for the remote host
        host: Hostname or IP address
        port: SSH port (default: 22)
        user: SSH username (optional, will use current user if not specified)
        description: Optional description of the host
    """
    config = load_config()

    if 'remote_hosts' not in config:
        config['remote_hosts'] = {}

    if not user:
        user = os.getenv('USER')

    # Build SSH connection string
    if port != 22:
        docker_host = f"ssh://{user}@{host}:{port}"
    else:
        docker_host = f"ssh://{user}@{host}"

    config['remote_hosts'][name] = {
        'host': host,
        'port': port,
        'user': user,
        'docker_host': docker_host,
        'description': description or f"Remote Docker host at {host}"
    }

    save_config(config)
    logging.info(f"Added remote host '{name}': {docker_host}")

def remove_remote_host(name):
    """
    Remove a named remote host configuration.

    Args:
        name: Name/alias of the remote host to remove
    """
    config = load_config()

    if 'remote_hosts' not in config or name not in config['remote_hosts']:
        raise ValueError(f"Remote host '{name}' not found in configuration")

    del config['remote_hosts'][name]
    save_config(config)
    logging.info(f"Removed remote host '{name}'")

def list_remote_hosts():
    """
    List all configured remote hosts.

    Returns:
        dict: Dictionary of remote host configurations
    """
    config = load_config()
    return config.get('remote_hosts', {})

def get_remote_host(name):
    """
    Get a specific remote host configuration.

    Args:
        name: Name/alias of the remote host

    Returns:
        str: Docker host connection string

    Raises:
        ValueError: If remote host not found
    """
    config = load_config()
    remote_hosts = config.get('remote_hosts', {})

    if name not in remote_hosts:
        raise ValueError(f"Remote host '{name}' not found in configuration")

    return remote_hosts[name]['docker_host']

def get_default_host():
    """
    Get the default Docker host (either configured or None for local).

    Returns:
        str or None: Docker host connection string
    """
    config = load_config()

    # Check if a default host is set
    default_host_name = config.get('default_host')
    if default_host_name:
        try:
            return get_remote_host(default_host_name)
        except ValueError:
            logging.warning(f"Default host '{default_host_name}' not found, using local")
            return None

    # Check if docker_host is set directly
    return config.get('docker_host')

def set_default_host(name):
    """
    Set a named remote host as the default.

    Args:
        name: Name/alias of the remote host, or None to use local
    """
    config = load_config()

    if name:
        # Verify the host exists
        remote_hosts = config.get('remote_hosts', {})
        if name not in remote_hosts:
            raise ValueError(f"Remote host '{name}' not found in configuration")
        config['default_host'] = name
    elif 'default_host' in config:
        del config['default_host']

    save_config(config)
    logging.info(f"Set default host to '{name}'")
