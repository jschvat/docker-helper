#!/usr/bin/env python3
"""
Test script to verify all services are loaded correctly
"""

import core
import os

def test_service_loading():
    """Test that all service YAML files are loaded"""
    print("Testing service loading...\n")

    # Get list of YAML files
    services_dir = 'services'
    if not os.path.exists(services_dir):
        print(f"ERROR: {services_dir} directory not found!")
        return

    yaml_files = [f for f in os.listdir(services_dir) if f.endswith('.yml')]
    print(f"Found {len(yaml_files)} YAML files in {services_dir}:")
    for f in sorted(yaml_files):
        print(f"  - {f}")

    print("\n" + "="*60 + "\n")

    # Load services through core
    available_services = core.get_available_services()
    print(f"Loaded {len(available_services)} services:\n")

    for service in sorted(available_services, key=lambda s: s['name']):
        name = service.get('name', 'UNKNOWN')
        desc = service.get('description', 'No description')
        image = service.get('image', 'No image')

        print(f"Service: {name}")
        print(f"  Description: {desc}")
        print(f"  Image: {image}")
        print()

    print("="*60 + "\n")

    # Test search functionality
    print("Testing search functionality:\n")

    test_searches = ['postgres', 'postgresql', 'sql', 'database', 'nginx', 'web']

    for search_term in test_searches:
        matches = []
        for service in available_services:
            name = service.get('name', '').lower()
            desc = service.get('description', '').lower()

            if search_term.lower() in name or search_term.lower() in desc:
                matches.append(service['name'])

        print(f"Search '{search_term}': {len(matches)} matches")
        if matches:
            for match in matches:
                print(f"  - {match}")
        print()

if __name__ == '__main__':
    test_service_loading()
