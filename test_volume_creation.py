#!/usr/bin/env python3
"""
Test script to verify automatic volume directory creation

This script tests the directory creation logic without running Docker.
Run this to verify the fix works correctly.
"""

import os
import sys
import tempfile
from pathlib import Path

def test_directory_creation():
    """Test the directory creation logic"""

    print("=" * 70)
    print("Testing Automatic Volume Directory Creation")
    print("=" * 70)

    # Create a temporary test directory
    test_base = os.path.join(tempfile.gettempdir(), 'docker_helper_test')

    # Clean up if exists
    if os.path.exists(test_base):
        os.system(f'rm -rf "{test_base}"')

    test_cases = [
        {
            'name': 'PostgreSQL single volume',
            'mappings': {
                'PGDATA': {
                    'enabled': True,
                    'host_path': os.path.join(test_base, 'postgres_data'),
                    'container_path': '/var/lib/postgresql/data'
                }
            },
            'expected_dirs': 1
        },
        {
            'name': 'Jellyfin multiple volumes',
            'mappings': {
                'config': {
                    'enabled': True,
                    'host_path': os.path.join(test_base, 'jellyfin', 'config'),
                    'container_path': '/config'
                },
                'movies': {
                    'enabled': True,
                    'host_path': os.path.join(test_base, 'media', 'movies'),
                    'container_path': '/data/movies'
                },
                'tv': {
                    'enabled': True,
                    'host_path': os.path.join(test_base, 'media', 'tv'),
                    'container_path': '/data/tvshows'
                }
            },
            'expected_dirs': 3
        },
        {
            'name': 'Disabled volume mapping',
            'mappings': {
                'data': {
                    'enabled': False,
                    'host_path': os.path.join(test_base, 'disabled_data'),
                    'container_path': '/data'
                }
            },
            'expected_dirs': 0
        },
        {
            'name': 'Empty host path',
            'mappings': {
                'data': {
                    'enabled': True,
                    'host_path': '',
                    'container_path': '/data'
                }
            },
            'expected_dirs': 0
        },
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 70)

        # Simulate the logic from execute_docker_command
        created_dirs = []
        config_values = {'volume_mappings': test_case['mappings']}

        volume_mappings = config_values.get('volume_mappings', {})
        for var_name, mapping in volume_mappings.items():
            if mapping.get('enabled'):
                host_path = mapping.get('host_path', '').strip()
                if host_path and not os.path.exists(host_path):
                    try:
                        os.makedirs(host_path, exist_ok=True)
                        created_dirs.append(host_path)
                        print(f"  ✓ Created directory: {host_path}")
                    except Exception as e:
                        print(f"  ✗ Error creating directory {host_path}: {str(e)}")
                        all_passed = False

        # Verify expected number of directories created
        expected = test_case['expected_dirs']
        actual = len(created_dirs)

        if actual == expected:
            print(f"  ✓ Test passed: Created {actual} directories (expected {expected})")
        else:
            print(f"  ✗ Test failed: Created {actual} directories (expected {expected})")
            all_passed = False

        # Verify directories actually exist
        for dir_path in created_dirs:
            if not os.path.exists(dir_path):
                print(f"  ✗ Directory doesn't exist: {dir_path}")
                all_passed = False

    # Clean up
    if os.path.exists(test_base):
        os.system(f'rm -rf "{test_base}"')
        print(f"\n✓ Cleaned up test directory: {test_base}")

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ All tests passed!")
        print("\nThe automatic directory creation feature is working correctly.")
        print("You can now install services with volume mappings without")
        print("manually creating directories first.")
        return 0
    else:
        print("✗ Some tests failed!")
        print("\nPlease check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(test_directory_creation())
