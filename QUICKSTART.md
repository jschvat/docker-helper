# Docker Helper - Quick Start Guide

## 🚀 Getting Started in 60 Seconds

### 1. Launch the Application
```bash
cd /media/jason/Array21/Development/claude/docker_helper
python main.py --gui
```

### 2. Your First Look

The application has 3 main sections:

```
┌─────────────────────────────────────────────────────┐
│  Docker Container Manager                           │
│  Manage Docker containers and services              │
├──────────────────┬──────────────────────────────────┤
│ Available        │ Running Containers      [2 run.] │
│ Services         │                                   │
│ [Search...]      │ [Search...]                      │
│                  │                                   │
│ ☐ bazarr         │ ID    Name    Status   Actions   │
│   Subtitle mgmt  │ abc.. nginx   running  ▶↻⏹📋💾🗑 │
│                  │ def.. mysql   running  ▶↻⏹📋💾🗑 │
├──────────────────┴──────────────────────────────────┤
│ Command Output                             [Clear]  │
│ >                                                    │
└─────────────────────────────────────────────────────┘
```

## 📋 Essential Actions

### View Container Logs
**Option 1**: Click the 📋 button
**Option 2**: Right-click container → "📋 View Logs"

```
┌────────────────────────────────────┐
│ Logs: nginx              [Refresh] │
│                           [Close]  │
├────────────────────────────────────┤
│ Tail lines: [100▼]  ☑ Timestamps  │
├────────────────────────────────────┤
│ 2025-10-15T04:19:13Z Starting...  │
│ 2025-10-15T04:19:14Z Ready        │
│                                    │
└────────────────────────────────────┘
```

### Open Terminal Inside Container
1. **Right-click** on any container
2. Click **"🖥 Open Terminal in Container"**
3. New terminal window opens
4. You're now inside the container!

```bash
# Example session
/ # ls
bin  etc  home  lib  ...
/ # ps aux
PID  USER     COMMAND
1    root     nginx
/ # exit
```

### Backup a Container
1. Click the **💾 button** (or right-click → "💾 Backup")
2. Choose backup type:
   - **Quick**: Commit to Image
   - **Archive**: Export to TAR
   - **Complete**: Full Backup ⭐ (recommended)
3. Select backup location
4. Click "Execute Backup"

```
Full Backup includes:
✓ Container filesystem
✓ All volume data
✓ Recreation script (recreate.sh)
```

### Manage Containers
Click the action buttons:
- **▶** Start
- **↻** Restart
- **⏹** Stop (asks for confirmation)
- **🗑** Remove (asks for confirmation)

## 🎯 Common Tasks

### Install a New Service
1. Find service in "Available Services"
2. **Check the checkbox** next to it
3. Click **"Install"** button (bottom)
4. Configure settings in dialog
5. Click **"Preview Command"** to see what will run
6. Click **"Install"** to execute

### Check Container Details
**Option 1**: Double-click on container row
**Option 2**: Right-click → "ℹ View Details"

Shows:
- Full ID, Name, Image
- Status and Uptime
- **Volumes** (all mounted paths)
- **Environment Variables**
- **Network Settings** (IP, MAC)

### Search for Containers
1. Use search box above containers list
2. Type container name, ID, status, or image
3. List filters in real-time

## 🔥 Pro Tips

### 1. Right-Click is Your Friend
Right-click on any container for quick access to:
- Open Terminal 🖥
- View Details ℹ
- View Logs 📋
- Backup 💾

### 2. Refresh Logs While Dialog is Open
In the logs dialog, click **"Refresh"** button to update logs without closing the dialog.

### 3. Full Backup Before Major Changes
Before updating or modifying a container:
1. Right-click → "💾 Backup"
2. Select "Full Backup"
3. Enable all options
4. Execute

You'll get everything needed to restore if something goes wrong!

### 4. Use the Recreation Script
After a full backup, navigate to the backup folder:
```bash
cd /tmp/container-name_20251015_123456/
cat recreate.sh  # View the script
./recreate.sh    # Recreate the container
```

### 5. Copy Container ID/Name Quickly
- **View Details** dialog has selectable text
- Select and copy with Ctrl+C

## 📦 Test Environment

### Create Test Containers

**Log Generator** (for testing logs feature):
```bash
docker run -d --name test-logs-container \
  alpine sh -c 'while true; do echo "Log at $(date)"; sleep 2; done'
```

**Web Server** (for testing terminal feature):
```bash
docker run -d --name test-nginx -p 8080:80 nginx:alpine
```

### Test the Features

1. **Logs**: Click 📋 on test-logs-container
   - Should see logs updating every 2 seconds
   - Try different tail line counts

2. **Terminal**: Right-click test-nginx → Open Terminal
   - Try: `ls /usr/share/nginx/html`
   - Try: `cat /etc/nginx/nginx.conf`

3. **Backup**: Click 💾 on test-nginx
   - Test "Full Backup" type
   - Check backup folder afterward

### Cleanup Test Containers
```bash
docker rm -f test-logs-container test-nginx
```

## ⚡ Keyboard Shortcuts

Currently available:
- **Double-click**: View container details
- **Ctrl+C**: Copy from dialogs (where text is selectable)

Future shortcuts (planned):
- Ctrl+T: Open terminal
- Ctrl+L: View logs
- Ctrl+R: Refresh view

## 🆘 Troubleshooting

### "No supported terminal emulator found"
Install a terminal:
```bash
# Ubuntu/Debian
sudo apt install gnome-terminal

# Fedora
sudo dnf install gnome-terminal

# Arch
sudo pacman -S gnome-terminal
```

### Terminal closes immediately
The container might not have `/bin/sh`. Try:
```bash
# Manually with bash
docker exec -it container_name /bin/bash

# Or ash (Alpine)
docker exec -it container_name /bin/ash
```

### Can't see any containers
Make sure Docker is running:
```bash
docker ps  # Should list containers
systemctl status docker  # Check Docker service
```

### Backup permission errors
Ensure backup directory is writable:
```bash
mkdir -p /tmp/my-backups
chmod 755 /tmp/my-backups
```

## 📚 Learn More

- **Full Features**: See `FEATURES_SUMMARY.md`
- **Backup Guide**: See `BACKUP_TESTING_GUIDE.md`
- **Logs Feature**: See `LOGS_FEATURE.md`
- **Context Menu**: See `CONTEXT_MENU_FEATURE.md`

## 🎓 Next Steps

### Beginner
1. ✅ Launch the app
2. ✅ View some container logs
3. ✅ Try opening a terminal
4. ✅ Create a backup

### Intermediate
1. Install a service from the list
2. Configure custom ports and variables
3. Use full backup with volumes
4. Test the recreation script

### Advanced
1. Write custom service YAML files
2. Script backups with cron
3. Manage multiple hosts
4. Integrate with monitoring tools

## 🔧 Configuration

### Service Files
Add custom services in `services/` directory:

```yaml
# services/myapp.yml
name: myapp
description: "My custom application"
image: myapp:latest

variables:
  - name: APP_PORT
    label: "Application Port"
    type: number
    default: 3000

ports:
  - name: "HTTP"
    host: 3000
    container: 3000
    protocol: "tcp"
```

Then restart the app to see your service!

## 💡 Best Practices

### ✅ DO
- Use Full Backup before major changes
- Enable "Pause during backup" for databases
- Save recreation scripts
- Use search to find containers quickly
- Right-click for quick actions

### ❌ DON'T
- Don't remove containers without backing up
- Don't forget to check logs after errors
- Don't run terminal commands you don't understand
- Don't backup to same disk as Docker data

## 🎉 You're Ready!

Start by:
1. **Right-clicking a container** → Try "Open Terminal"
2. **Clicking 📋** → View some logs
3. **Clicking 💾** → Create a backup

Have fun managing your containers! 🐳
