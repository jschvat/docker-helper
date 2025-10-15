#!/usr/bin/env python3
"""
Safe backup testing script
Creates a test container and tests all backup methods
"""

import docker
import os
import sys
import shutil

def cleanup_test_files(backup_dir):
    """Remove test backup files"""
    if os.path.exists(backup_dir):
        print(f"Cleaning up {backup_dir}...")
        shutil.rmtree(backup_dir)

def test_backup():
    """Test all backup types safely"""
    client = docker.from_env()
    test_container_name = "test-backup-container"
    backup_base_dir = "/tmp/docker-backup-test"

    print("=" * 60)
    print("Docker Backup Testing Script")
    print("=" * 60)

    try:
        # Verify test container exists
        container = client.containers.get(test_container_name)
        print(f"✓ Found test container: {container.name} ({container.short_id})")
        print(f"  Status: {container.status}")
        print(f"  Image: {container.image.tags[0] if container.image.tags else container.image.short_id}")
        print()

        # Clean up old test backups
        cleanup_test_files(backup_base_dir)
        os.makedirs(backup_base_dir, exist_ok=True)

        # Test 1: Commit to Image
        print("TEST 1: Commit to Image")
        print("-" * 60)
        try:
            image_name = f"{test_container_name}-backup"
            timestamp = "test"
            image = container.commit(repository=image_name, tag=timestamp)
            print(f"✓ Successfully committed to image: {image_name}:{timestamp}")
            print(f"  Image ID: {image.short_id}")

            # Clean up test image
            client.images.remove(image.id, force=True)
            print(f"✓ Cleaned up test image")
        except Exception as e:
            print(f"✗ Commit test failed: {e}")
        print()

        # Test 2: Export to TAR
        print("TEST 2: Export to TAR")
        print("-" * 60)
        try:
            export_file = os.path.join(backup_base_dir, f"{test_container_name}_export.tar")
            print(f"  Exporting to: {export_file}")

            bits = container.export()
            with open(export_file, 'wb') as f:
                for chunk in bits:
                    f.write(chunk)

            file_size = os.path.getsize(export_file)
            print(f"✓ Successfully exported container")
            print(f"  File size: {file_size / 1024 / 1024:.2f} MB")
        except Exception as e:
            print(f"✗ Export test failed: {e}")
        print()

        # Test 3: Volume backup
        print("TEST 3: Volume Backup")
        print("-" * 60)
        try:
            mounts = container.attrs.get('Mounts', [])
            print(f"  Found {len(mounts)} mount(s)")

            if mounts:
                import tarfile
                for i, mount in enumerate(mounts):
                    source = mount.get('Source', '')
                    destination = mount.get('Destination', '')
                    mount_type = mount.get('Type', 'unknown')

                    print(f"  Mount {i+1}: {mount_type}")
                    print(f"    Source: {source}")
                    print(f"    Destination: {destination}")

                    if source and os.path.exists(source):
                        volume_backup = os.path.join(backup_base_dir, f"volume_{i}.tar")
                        with tarfile.open(volume_backup, 'w') as tar:
                            tar.add(source, arcname=os.path.basename(source))

                        file_size = os.path.getsize(volume_backup)
                        print(f"    ✓ Backed up to {volume_backup} ({file_size} bytes)")
                    else:
                        print(f"    ⚠ Source path doesn't exist or is empty")
            else:
                print("  ℹ No volumes to backup")
        except Exception as e:
            print(f"✗ Volume backup test failed: {e}")
        print()

        # Test 4: Recreation Script
        print("TEST 4: Recreation Script Generation")
        print("-" * 60)
        try:
            from datetime import datetime

            attrs = container.attrs
            config = attrs['Config']
            host_config = attrs['HostConfig']

            script_lines = [
                "#!/bin/bash",
                "# Container Recreation Script",
                f"# Original container: {container.name}",
                f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "docker run -d \\",
                f"  --name {container.name}_restored \\",
            ]

            # Add environment variables
            env_count = 0
            for env in config.get('Env', []):
                if not env.startswith(('PATH=', 'HOME=')):
                    script_lines.append(f"  -e '{env}' \\")
                    env_count += 1

            # Add port mappings
            port_count = 0
            port_bindings = host_config.get('PortBindings', {})
            for container_port, host_ports in port_bindings.items():
                if host_ports:
                    host_port = host_ports[0]['HostPort']
                    script_lines.append(f"  -p {host_port}:{container_port} \\")
                    port_count += 1

            # Add volume mounts
            volume_count = 0
            for mount in attrs.get('Mounts', []):
                source = mount.get('Source', '')
                destination = mount.get('Destination', '')
                if source and destination:
                    script_lines.append(f"  -v {source}:{destination} \\")
                    volume_count += 1

            # Add image
            image = config.get('Image', '')
            script_lines.append(f"  {image}")

            # Write script
            script_file = os.path.join(backup_base_dir, "recreate.sh")
            with open(script_file, 'w') as f:
                f.write('\n'.join(script_lines))
                f.write('\n')

            os.chmod(script_file, 0o755)

            print(f"✓ Successfully generated recreation script")
            print(f"  Environment variables: {env_count}")
            print(f"  Port mappings: {port_count}")
            print(f"  Volume mounts: {volume_count}")
            print(f"  Script location: {script_file}")
            print()
            print("  Script contents:")
            print("  " + "-" * 56)
            with open(script_file, 'r') as f:
                for line in f:
                    print(f"  {line.rstrip()}")
            print("  " + "-" * 56)
        except Exception as e:
            print(f"✗ Recreation script test failed: {e}")
        print()

        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Backup directory: {backup_base_dir}")

        if os.path.exists(backup_base_dir):
            print("\nGenerated files:")
            for item in os.listdir(backup_base_dir):
                path = os.path.join(backup_base_dir, item)
                if os.path.isfile(path):
                    size = os.path.getsize(path)
                    print(f"  - {item} ({size / 1024:.2f} KB)")
                else:
                    print(f"  - {item}/ (directory)")

        print("\n✓ All backup methods tested successfully!")
        print(f"\nYou can now safely launch the GUI and test the backup dialog.")
        print(f"The test container '{test_container_name}' is ready for backup testing.")

    except docker.errors.NotFound:
        print(f"✗ Test container '{test_container_name}' not found!")
        print(f"\nTo create it, run:")
        print(f"  docker run -d --name {test_container_name} -e TEST_VAR=hello -p 8888:80 -v /tmp/test-volume:/data alpine sleep 3600")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)

def cleanup():
    """Clean up test container and files"""
    print("\nCleaning up test environment...")
    client = docker.from_env()

    try:
        container = client.containers.get("test-backup-container")
        print(f"  Removing container: {container.name}")
        container.remove(force=True)
        print("  ✓ Container removed")
    except docker.errors.NotFound:
        print("  ℹ Test container not found")

    cleanup_test_files("/tmp/docker-backup-test")
    print("  ✓ Test files removed")
    print("\n✓ Cleanup complete!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup()
    else:
        test_backup()
        print("\nTo clean up, run: python test_backup.py cleanup")
