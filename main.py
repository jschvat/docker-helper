import argparse
import core

def main():
    parser = argparse.ArgumentParser(description='A Docker management tool with reverse proxy capabilities.')
    parser.add_argument('--gui', action='store_true', help='Launch the GTK GUI.')
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

    args = parser.parse_args()

    if args.gui:
        import gui
        gui.main()
        return

    if not args.action:
        parser.print_help()
        return

    try:
        client = core.get_client()
    except ConnectionError as e:
        print(e)
        return

    if args.action == 'install':
        for service_name in args.services:
            print(core.install_service(client, service_name))
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