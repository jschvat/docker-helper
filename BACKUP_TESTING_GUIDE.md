# Backup Feature Testing Guide

## Overview
The Docker Helper now includes comprehensive container backup functionality with three backup types:
- **Commit to Image**: Quick filesystem snapshot (no volumes)
- **Export to TAR**: Full container export to archive (no volumes)
- **Full Backup**: Complete backup including container, volumes, and recreation script

## Safe Testing Setup

### 1. Test Container Created
A safe test container has been created for testing:
```bash
Container: test-backup-container
ID: 3f3dfbbfe511
Image: alpine:latest
Ports: 8888:80
Volume: /tmp/test-volume:/data
Environment: TEST_VAR=hello
```

### 2. Automated Testing
Run the automated test script to verify all backup methods:
```bash
python test_backup.py
```

This will test:
- ✓ Commit to image
- ✓ Export to TAR
- ✓ Volume backup
- ✓ Recreation script generation

### 3. GUI Testing Steps

#### Step 1: Launch the GUI
```bash
python main.py --gui
```

#### Step 2: Locate the Test Container
- Look in the "Running Containers" panel on the right
- Find the row with "test-backup-container"
- You should see 5 action buttons: ▶ ↻ ⏹ 💾 🗑

#### Step 3: Test the Backup Dialog
1. Click the **💾 (Backup)** button
2. The backup dialog will open with three options

#### Step 4: Test Each Backup Type

**Test A: Commit to Image**
- Select "Commit to Image (filesystem snapshot, no volumes)"
- Leave default backup location: `/tmp/test-backup-container-backup`
- Uncheck "Pause container during backup" (for speed)
- Click "Execute Backup"
- Check output panel for success message
- Verify image created: `docker images | grep test-backup-container`

**Test B: Export to TAR**
- Click 💾 again
- Select "Export to TAR (full container export, no volumes)"
- Set backup location: `/tmp/test-export-backup`
- Check "Compress backup files"
- Click "Execute Backup"
- Verify file created: `ls -lh /tmp/test-export-backup/*.tar.gz`

**Test C: Full Backup**
- Click 💾 again
- Select "Full Backup (container + volumes + run command)"
- Set backup location: `/tmp/test-full-backup`
- Check all options:
  - ✓ Pause container during backup
  - ✓ Compress backup files
  - ✓ Save container recreation script
- Click "Execute Backup"
- Verify backup directory structure:
  ```bash
  ls -lh /tmp/test-full-backup/
  # Should contain a timestamped directory
  ```

#### Step 5: Verify Full Backup Contents
```bash
# Navigate to the timestamped backup directory
cd /tmp/test-full-backup/test-backup-container_*

# You should see:
# - container.tar.gz (compressed container export)
# - volumes/ (directory with volume backups)
# - recreate.sh (executable recreation script)

# Inspect the recreation script
cat recreate.sh
```

#### Step 6: Test Recreation Script
```bash
# Make sure you're in the backup directory
cd /tmp/test-full-backup/test-backup-container_*/

# Review the script (it creates a new container with "_restored" suffix)
cat recreate.sh

# Optional: Test the script (creates test-backup-container_restored)
./recreate.sh

# Verify the restored container
docker ps -a | grep restored
```

## Expected Results

### Commit to Image
- Output: "✓ Committed to image: test-backup-container-backup:[timestamp]"
- Verify: `docker images` shows the new image
- File location: Docker's image storage

### Export to TAR
- Output: "✓ Container exported successfully"
- File: `/tmp/test-export-backup/test-backup-container_[timestamp].tar.gz`
- Size: ~8-10 MB (compressed alpine container)

### Full Backup
- Output shows:
  - "📦 Exporting container..."
  - "✓ Container exported"
  - "💾 Backing up 1 volume(s)..."
  - "✓ Volume: /data"
  - "✓ Volumes backed up"
  - "✓ Recreation script saved: recreate.sh"
  - "📁 Full backup location: [path]"

- Directory structure:
  ```
  test-backup-container_[timestamp]/
  ├── container.tar.gz
  ├── volumes/
  │   └── volume_0_data.tar.gz
  └── recreate.sh
  ```

## Safety Features

### Pause During Backup
- When enabled, the container is paused before backup
- Ensures data consistency
- Automatically resumed after backup completes
- Output shows: "⏸ Container paused for backup" and "▶ Container resumed"

### Non-Destructive
- All backup operations are **read-only**
- Original container is never modified
- Original data is never deleted
- Recreation script uses a different name (appends "_restored")

### Error Handling
- If backup fails, container is automatically resumed
- Clear error messages in the output panel
- Partial backups are indicated

## Testing Tooltips
Hover over the action buttons to see tooltips:
- ▶ = "Start container"
- ↻ = "Restart container"
- ⏹ = "Stop container"
- 💾 = "Backup container (commit to image)"
- 🗑 = "Remove container"

## Cleanup After Testing

### Option 1: Using the cleanup script
```bash
python test_backup.py cleanup
```

### Option 2: Manual cleanup
```bash
# Remove test container
docker rm -f test-backup-container

# Remove any restored test containers
docker rm -f test-backup-container_restored

# Remove test backups
rm -rf /tmp/test-backup-container-backup
rm -rf /tmp/test-export-backup
rm -rf /tmp/test-full-backup
rm -rf /tmp/docker-backup-test

# Remove test volume
rm -rf /tmp/test-volume

# Remove test backup images
docker rmi $(docker images -q test-backup-container-backup)
```

## Production Use

### Best Practices
1. **Always use Full Backup** for production containers with important data
2. **Enable "Pause during backup"** for databases and stateful applications
3. **Use compression** to save disk space
4. **Save recreation script** to document exact container configuration
5. **Store backups on different disk/server** than the running container

### Recommended Backup Locations
- Local: `/backup/docker/[container-name]/[date]`
- Network: `/mnt/nas/docker-backups/[container-name]/[date]`
- Cloud: Sync backup directory to cloud storage after completion

### Backup Frequency
- Critical services: Daily full backups
- Development: Weekly or before major changes
- Production databases: Daily with retention policy

## Troubleshooting

### "Permission denied" errors
- Check that backup directory is writable
- For volume backups, ensure read access to volume paths
- May need sudo for system-managed volumes

### Large backup files
- Use compression option
- Consider excluding unnecessary volumes
- For very large containers, consider incremental backups

### Container won't pause
- Check if container supports pause (some don't)
- Disable "Pause during backup" option
- Stop container manually if needed

### Script won't execute
- Verify `recreate.sh` has execute permissions: `chmod +x recreate.sh`
- Check script for correct paths
- Update volume paths if restoring to different location

## Feature Locations in Code

- Backup dialog: `gui.py:1089-1206`
- Backup execution: `gui.py:1224-1345`
- Recreation script: `gui.py:1347-1403`
- Action buttons: `gui.py:422-468`
- Tooltips: `gui.py:493-521`

## Future Enhancements (Not Yet Implemented)

The following features are not yet implemented but could be added:
- Restore functionality from backups
- Scheduled/automated backups
- Backup encryption
- Incremental backups
- Remote backup destinations (S3, FTP, etc.)
- Backup verification
- Multiple backup profiles per container
