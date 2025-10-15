# Right-Click Context Menu Feature

## Overview
Added a right-click context menu to container rows in the Running Containers view, providing quick access to common container operations including opening an interactive terminal inside the container.

## Features

### Access
- **Trigger**: Right-click on any container row in the Running Containers view
- **Works on**: Any column (ID, Name, Status, Image, Uptime, Ports, Network, Actions)
- **Benefit**: Quick access to operations without using the action buttons

### Context Menu Options

```
┌─────────────────────────────────────┐
│ 🖥 Open Terminal in Container      │
│ ℹ View Details                      │
├─────────────────────────────────────┤
│ 📋 View Logs                        │
│ 💾 Backup Container                 │
└─────────────────────────────────────┘
```

## Menu Actions

### 1. 🖥 Open Terminal in Container

**Description**: Opens a new terminal window with an interactive shell inside the container

**Implementation**:
- Automatically detects available terminal emulators on the system
- Executes `docker exec -it <container_id> /bin/sh`
- Launches terminal in background (non-blocking)

**Supported Terminal Emulators** (in order of preference):
1. `gnome-terminal` (GNOME)
2. `xterm` (Universal X terminal)
3. `konsole` (KDE)
4. `xfce4-terminal` (XFCE)
5. `mate-terminal` (MATE)
6. `terminator` (Advanced terminal)

**Fallback Behavior**:
- If no supported terminal is found, shows error dialog
- Provides manual command: `docker exec -it <container_id> /bin/sh`

**Example Usage**:
1. Right-click on a running container
2. Click "🖥 Open Terminal in Container"
3. New terminal window opens with shell prompt inside container
4. Type commands interactively (e.g., `ls`, `ps`, `env`)
5. Exit with `exit` or Ctrl+D

### 2. ℹ View Details

**Description**: Opens the full container details dialog

**Information Displayed**:
- Container ID
- Container Name
- Image
- Status
- Uptime
- Volumes (with paths)
- Environment Variables
- Network Settings (IP, MAC addresses)

**Same as**: Double-clicking on a container row

### 3. 📋 View Logs

**Description**: Opens the logs viewer dialog

**Features**:
- Adjustable tail lines (10-10,000)
- Timestamp toggle
- Refresh button
- Scrollable, selectable text

**Same as**: Clicking the 📋 button in Actions column

### 4. 💾 Backup Container

**Description**: Opens the comprehensive backup dialog

**Backup Types**:
- Commit to Image
- Export to TAR
- Full Backup (container + volumes + recreation script)

**Same as**: Clicking the 💾 button in Actions column

## Implementation Details

### Code Location
- **Context Menu**: `show_container_context_menu()` in gui.py:1217-1245
- **Right-click Handler**: `on_container_button_press()` in gui.py:533-588 (lines 573-586)
- **Terminal Launcher**: `open_container_terminal()` in gui.py:1294-1331

### Terminal Detection Logic

```python
terminals = [
    ('gnome-terminal', ['gnome-terminal', '--', 'docker', 'exec', '-it', container_id, '/bin/sh']),
    ('xterm', ['xterm', '-e', f'docker exec -it {container_id} /bin/sh']),
    ('konsole', ['konsole', '-e', f'docker exec -it {container_id} /bin/sh']),
    # ... more terminals
]

# Find first available
for term_name, term_cmd in terminals:
    if shutil.which(term_name.split()[0]):
        terminal_found = term_cmd
        break
```

### Docker exec Command

```bash
docker exec -it <container_id> /bin/sh
```

**Flags**:
- `-i`: Interactive (keep STDIN open)
- `-t`: Allocate pseudo-TTY (terminal)

**Shell Priority**:
Currently uses `/bin/sh` (available in all containers)

**Future Enhancement**: Try shells in order:
1. `/bin/bash` (if available)
2. `/bin/sh` (fallback)
3. `/bin/ash` (Alpine containers)

## Testing

### Test Cases

1. **Basic Terminal Opening**
   ```bash
   # In GUI:
   - Right-click test-backup-container
   - Click "Open Terminal"
   # In terminal window:
   - Should see shell prompt
   - Run: ls
   - Run: pwd
   - Run: env
   ```

2. **Multiple Terminals**
   - Right-click container A → Open Terminal
   - Right-click container B → Open Terminal
   - Verify two separate terminal windows open

3. **Container Without bash**
   ```bash
   # Alpine containers only have /bin/sh
   docker run -d --name test-alpine alpine sleep 3600
   # Right-click, open terminal → should work with /bin/sh
   ```

4. **Menu Display**
   - Right-click on ID column
   - Right-click on Name column
   - Right-click on Actions column
   - All should show same context menu

5. **No Terminal Available**
   ```bash
   # Temporarily hide terminal
   sudo mv /usr/bin/gnome-terminal /usr/bin/gnome-terminal.bak
   # Right-click, open terminal → should show error with manual command
   # Restore:
   sudo mv /usr/bin/gnome-terminal.bak /usr/bin/gnome-terminal
   ```

### Test Containers

Use existing test containers:
```bash
# Container with /bin/sh
docker ps --filter name=test-backup-container

# Container with logs
docker ps --filter name=test-logs-container
```

## User Experience

### Before (Without Context Menu)
1. User wants to run commands in container
2. Must click tiny 📋 logs button to see output
3. Or switch to terminal and type `docker exec -it <container> /bin/sh`
4. Must remember/copy container ID or name

### After (With Context Menu)
1. User right-clicks on container row
2. Clicks "Open Terminal"
3. New terminal window opens instantly
4. Interactive shell ready for commands

**Time Saved**: ~10-15 seconds per operation

## Error Handling

### Scenarios Handled

1. **No Terminal Emulator Found**
   - Shows clear error dialog
   - Lists supported terminals
   - Provides manual command

2. **Container Not Running**
   - Docker will show error: "container is not running"
   - Displayed in output panel

3. **Terminal Launch Failure**
   - Catches subprocess exceptions
   - Shows error message in output panel

4. **Container Has No Shell**
   - Some minimal containers don't have `/bin/sh`
   - Docker error: "executable file not found"

## CLI Equivalents

### Open Terminal
```bash
# Find container ID/name
docker ps

# Open interactive shell
docker exec -it container_name /bin/sh

# Or with bash if available
docker exec -it container_name /bin/bash
```

### Compare to Context Menu
- Context menu: 2 clicks (right-click + click)
- CLI: Type command + find/copy ID + press enter

## Future Enhancements

### Planned Features

1. **Shell Selection Dialog**
   - Let user choose shell: bash, sh, ash, zsh
   - Remember preference per container image

2. **Custom Command Execution**
   - Menu item: "Run Command..."
   - Input dialog for custom command
   - Example: `docker exec -it <container> python`

3. **Root vs User Shell**
   - Option to open shell as specific user
   - `docker exec -it -u root <container> /bin/sh`

4. **Working Directory Selection**
   - Menu item: "Open Terminal at..."
   - Select container directory
   - `docker exec -it -w /app <container> /bin/sh`

5. **Multiple Shells Per Container**
   - Submenu: "Open Terminal →"
     - As root
     - As container user
     - In /app directory
     - In /var/log directory

6. **Terminal Profile/Preferences**
   - Font size
   - Color scheme
   - Window size

### Advanced Features

1. **Embedded Terminal (VTE)**
   - Use GTK VTE widget
   - Terminal inside dialog window
   - No external terminal needed

2. **SSH-style Connection**
   - For remote Docker hosts
   - SSH tunnel + docker exec

3. **Container File Browser**
   - Menu item: "Browse Files"
   - GTK file chooser showing container filesystem
   - Upload/download files

4. **Quick Commands Submenu**
   - Submenu with common commands:
     - Show running processes (`ps aux`)
     - Show disk usage (`df -h`)
     - Show memory usage (`free -m`)
     - Tail logs (`tail -f /var/log/*`)

## Keyboard Shortcuts (Future)

Potential shortcuts for future implementation:
- `Ctrl+T`: Open terminal in selected container
- `Ctrl+L`: View logs of selected container
- `Ctrl+I`: View details of selected container
- `Shift+F10`: Show context menu (Windows-style)
- `Menu Key`: Show context menu

## Accessibility

The context menu enhances accessibility:
- **Mouse users**: Quick right-click access
- **Keyboard users**: (Future) Keyboard shortcut support
- **Screen readers**: Menu items have clear labels with emoji icons

## Security Considerations

### Safe by Design
- Uses Docker's built-in `exec` command
- Respects container user permissions
- No password/credential handling
- Terminal runs with user's Docker permissions

### Best Practices
- Don't run as root unless necessary
- Be careful with `docker exec` on production containers
- Terminal operations are logged by Docker

## Comparison to Docker Desktop

| Feature | Docker Desktop | Docker Helper |
|---------|---------------|---------------|
| Right-click menu | ✅ Yes | ✅ Yes |
| Open terminal | ✅ Yes | ✅ Yes |
| View logs | ✅ Yes | ✅ Yes |
| View details | ✅ Yes | ✅ Yes |
| Backup container | ❌ No | ✅ Yes |
| Context menu on all columns | ❌ No | ✅ Yes |
| Auto-detect terminals | ❌ No | ✅ Yes |
| Free & Open Source | ❌ No | ✅ Yes |

## Code Statistics

- Lines added: ~120
- Methods added: 6
  - `show_container_context_menu()`
  - `on_context_open_terminal()`
  - `on_context_view_details()`
  - `on_context_view_logs()`
  - `on_context_backup()`
  - `open_container_terminal()`
- Terminal emulators supported: 6
- Dependencies: shutil (for terminal detection)

## Documentation

- Feature file: `CONTEXT_MENU_FEATURE.md` (this file)
- Related files:
  - `LOGS_FEATURE.md` (logs viewer)
  - `BACKUP_TESTING_GUIDE.md` (backup feature)
- Code location: `gui.py:533-588, 1217-1331`
