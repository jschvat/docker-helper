import argparse
import core
import config

def main():
    parser = argparse.ArgumentParser(description='A Docker management tool with reverse proxy capabilities.')
    parser.add_argument('--gui', action='store_true', help='Launch the GTK GUI.')
    parser.add_argument('--host', '-H', dest='docker_host',
                        help='Docker host to connect to (e.g., ssh://user@host, ssh://user@host:port, tcp://host:port, or a saved remote name)')
    subparsers = parser.add_subparsers(dest='action')

    install_parser = subparsers.add_parser('install', help='Install services.')
    install_parser.add_argument('services', nargs='+', help='The services to install.')

    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall services.')
    uninstall_parser.add_argument('services', nargs='+', help='The services to uninstall.')

    start_parser = subparsers.add_parser('start', help='Start services.')
    start_parser.add_argument('services', nargs='+', help='The services to start.')

    stop_parser = subparsers.add_parser('stop', help='Stop services.')
    stop_parser.add_argument('services', nargs='+', help='The services to stop.')

    restart_parser = subparsers.add_parser('restart', help='Restart services.')
    restart_parser.add_argument('services', nargs='+', help='The services to restart.')

    status_parser = subparsers.add_parser('status', help='Show status of services.')
    status_parser.add_argument('services', nargs='*', help='The services to show the status of.')

    update_parser = subparsers.add_parser('update', help='Update services.')
    update_parser.add_argument('services', nargs='+', help='The services to update.')

    configure_parser = subparsers.add_parser('configure', help='Configure DuckDNS settings.')
    configure_parser.add_argument('--token', help='Your DuckDNS token.')
    configure_parser.add_argument('--domain', help='Your DuckDNS domain.')

    test_parser = subparsers.add_parser('test', help='Run a test container.')

    # Remote host management
    remote_parser = subparsers.add_parser('remote', help='Manage remote Docker hosts.')
    remote_subparsers = remote_parser.add_subparsers(dest='remote_action')

    add_remote_parser = remote_subparsers.add_parser('add', help='Add a remote Docker host.')
    add_remote_parser.add_argument('name', help='Name/alias for the remote host.')
    add_remote_parser.add_argument('host', help='Hostname or IP address.')
    add_remote_parser.add_argument('--user', help='SSH username (default: current user).')
    add_remote_parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22).')
    add_remote_parser.add_argument('--description', help='Optional description.')

    remove_remote_parser = remote_subparsers.add_parser('remove', help='Remove a remote Docker host.')
    remove_remote_parser.add_argument('name', help='Name/alias of the remote host to remove.')

    list_remote_parser = remote_subparsers.add_parser('list', help='List all remote Docker hosts.')

    set_default_parser = remote_subparsers.add_parser('set-default', help='Set default Docker host.')
    set_default_parser.add_argument('name', nargs='?', help='Name of remote host (omit for local).')

    args = parser.parse_args()

    if args.gui:
        import gui
        gui.main(docker_host=args.docker_host)
        return

    if not args.action:
        parser.print_help()
        return

    # Handle remote host management commands
    if args.action == 'remote':
        if args.remote_action == 'add':
            try:
                config.add_remote_host(
                    args.name,
                    args.host,
                    port=args.port,
                    user=args.user,
                    description=args.description
                )
                print(f"Remote host '{args.name}' added successfully.")
            except Exception as e:
                print(f"Error adding remote host: {e}")
            return
        elif args.remote_action == 'remove':
            try:
                config.remove_remote_host(args.name)
                print(f"Remote host '{args.name}' removed successfully.")
            except Exception as e:
                print(f"Error removing remote host: {e}")
            return
        elif args.remote_action == 'list':
            remote_hosts = config.list_remote_hosts()
            if not remote_hosts:
                print("No remote hosts configured.")
            else:
                print("Configured remote hosts:")
                for name, info in remote_hosts.items():
                    print(f"\n  {name}:")
                    print(f"    Host: {info['host']}")
                    print(f"    User: {info['user']}")
                    print(f"    Port: {info['port']}")
                    print(f"    Connection: {info['docker_host']}")
                    if info.get('description'):
                        print(f"    Description: {info['description']}")
            return
        elif args.remote_action == 'set-default':
            try:
                config.set_default_host(args.name)
                if args.name:
                    print(f"Default host set to '{args.name}'.")
                else:
                    print("Default host set to local.")
            except Exception as e:
                print(f"Error setting default host: {e}")
            return
        else:
            remote_parser.print_help()
            return

    # Resolve docker host (command line arg, saved remote name, or config default)
    docker_host = args.docker_host
    if docker_host:
        # Check if it's a saved remote name
        try:
            docker_host = config.get_remote_host(docker_host)
        except ValueError:
            # Not a saved name, treat as direct connection string
            pass
    else:
        # Use default from config
        docker_host = config.get_default_host()

    try:
        client = core.get_client(docker_host=docker_host)
        if docker_host:
            print(f"Connected to Docker host: {docker_host}")
    except ConnectionError as e:
        print(e)
        return

    if args.action == 'install':
        for service_name in args.services:
            try:
                # Load service configuration
                service_config = core.load_service_config(service_name)

                # Collect configuration values from user
                config_values = {}
                if 'variables' in service_config:
                    print(f"\nConfiguring {service_name}:")
                    print(f"Description: {service_config.get('description', 'No description available')}\n")

                    for variable in service_config['variables']:
                        var_name = variable['name']
                        var_label = variable.get('label', var_name)
                        var_description = variable.get('description', '')
                        var_default = variable.get('default', '')

                        # Prompt user for value
                        prompt = f"  {var_label}"
                        if var_description:
                            prompt += f" ({var_description})"
                        if var_default:
                            prompt += f" [default: {var_default}]"
                        prompt += ": "

                        user_input = input(prompt).strip()
                        config_values[var_name] = user_input if user_input else var_default

                # Install the service
                result = core.install_service(client, service_config, config_values)
                print(result)

            except FileNotFoundError:
                print(f"Error: Service configuration for '{service_name}' not found.")
            except Exception as e:
                print(f"Error installing {service_name}: {e}")
    elif args.action == 'uninstall':
        for service_name in args.services:
            print(core.uninstall_service(client, service_name))
    elif args.action == 'start':
        for service_name in args.services:
            print(core.start_service(client, service_name))
    elif args.action == 'stop':
        for service_name in args.services:
            print(core.stop_service(client, service_name))
    elif args.action == 'restart':
        for service_name in args.services:
            print(core.restart_service(client, service_name))
    elif args.action == 'status':
        print(core.get_status(client, args.services))
    elif args.action == 'update':
        for service_name in args.services:
            print(core.update_service(client, service_name))
    elif args.action == 'configure':
        print(core.handle_configure(args.token, args.domain))
    elif args.action == 'test':
        print(core.test_container(client))

if __name__ == '__main__':
    main()