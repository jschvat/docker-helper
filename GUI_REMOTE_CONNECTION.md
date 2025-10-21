# GUI Remote Connection Features

This document describes the remote connection features added to the docker_helper GUI.

## Connection Button

A **Connection** button has been added to the header bar (top right corner) that provides quick access to connection management.

### Features

When you click the Connection button, you'll see a dropdown menu with:

1. **Connect to Local Docker** - Switch back to your local Docker daemon
2. **Saved Remote Hosts** - Quick connect to any saved remote Docker hosts
3. **Custom Connection...** - Enter a custom connection string
4. **Manage Remote Hosts...** - Add, view, and remove saved remote hosts

## Connection Menu Options

### 1. Connect to Local Docker

Switches the current GUI session to connect to your local Docker daemon. All container lists and views will refresh automatically.

### 2. Saved Remote Hosts

If you have saved any remote hosts (either through the CLI or GUI), they will appear in this list. Click on any saved host to connect to it immediately.

Example menu items:
- Connect to production (192.168.1.100)
- Connect to staging (192.168.1.101)
- Connect to homelab (192.168.1.50)

### 3. Custom Connection

Opens a dialog where you can enter a custom Docker connection string:

**Supported formats:**
- `ssh://user@host` - SSH connection (port 22)
- `ssh://user@host:port` - SSH with custom port
- `tcp://host:port` - TCP connection

**Examples:**
```
ssh://user@192.168.1.100
ssh://user@example.com:2222
tcp://192.168.1.100:2375
```

After entering the connection string and clicking Connect, the GUI will attempt to connect to the remote Docker instance.

### 4. Manage Remote Hosts

Opens a comprehensive dialog for managing your saved remote Docker hosts.

#### Features:

**View All Saved Hosts:**
- See a list of all configured remote hosts
- View connection details for each host

**Add New Remote Host:**
1. Click "Add New Remote Host" button
2. Fill in the form:
   - **Name**: A friendly name (e.g., "production", "staging")
   - **Host**: IP address or hostname (e.g., "192.168.1.100")
   - **User**: SSH username (defaults to your current user)
   - **Port**: SSH port (defaults to 22)
   - **Description**: Optional description

3. Click Add to save

**Remove Remote Host:**
- Click the "Remove" button next to any saved host
- Confirm the deletion

All changes are saved to `~/.config/docker_helper/config.yml`.

## Connection Status

The GUI header displays the current connection status:

- **Local:** Shows "Connected to: Local Docker"
- **Remote:** Shows "Connected to: ssh://user@host:port"

This makes it easy to see at a glance which Docker instance you're managing.

## Switching Connections

When you switch to a different Docker host (local or remote):

1. The GUI attempts to connect to the new host
2. If successful:
   - The connection status is updated in the header
   - All container lists are refreshed
   - The service list is updated
   - A success message appears in the output view
3. If connection fails:
   - An error dialog is shown
   - The GUI remains connected to the previous host

## Usage Examples

### Example 1: Quick Connect to Production

1. Click the **Connection** button in the header
2. Select **Connect to production (192.168.1.100)** from the menu
3. The GUI connects and refreshes all views

### Example 2: Add a New Remote Host

1. Click the **Connection** button
2. Select **Manage Remote Hosts...**
3. Click **Add New Remote Host**
4. Fill in:
   - Name: `homelab`
   - Host: `192.168.1.50`
   - User: `docker`
   - Port: `22`
   - Description: `Home Lab Server`
5. Click **Add**
6. Close the management dialog
7. Click **Connection** again
8. Select **Connect to homelab (192.168.1.50)**

### Example 3: One-Time Custom Connection

1. Click the **Connection** button
2. Select **Custom Connection...**
3. Enter: `ssh://user@192.168.1.200:2222`
4. Click **Connect**
5. GUI connects to the custom host (not saved)

### Example 4: Return to Local Docker

1. Click the **Connection** button
2. Select **Connect to Local Docker**
3. GUI switches back to local Docker daemon

## Integration with CLI

The GUI and CLI share the same configuration file (`~/.config/docker_helper/config.yml`), so:

- Remote hosts added via CLI are available in the GUI
- Remote hosts added via GUI are available in the CLI
- Default host settings are shared

### CLI Commands for Reference:

```bash
# Add a remote host (available in GUI)
python3 main.py remote add production 192.168.1.100 --user john

# List all remote hosts
python3 main.py remote list

# Launch GUI connected to a specific host
python3 main.py --gui --host production
```

## Visual Design

The Connection button features:
- Clean, modern design with icon and label
- Semi-transparent background that stands out on the gradient header
- Hover effect for better interactivity
- Integrated seamlessly into the header layout

## Technical Details

### Connection Process

1. User selects a connection from the menu
2. `reconnect_to_host(docker_host)` is called
3. New Docker client is created with `core.get_client(docker_host=docker_host)`
4. Connection is tested with `client.ping()`
5. If successful:
   - Old client is replaced
   - `docker_host` attribute is updated
   - Header subtitle is updated
   - All views are refreshed
6. If failed:
   - Error dialog is shown
   - Previous connection remains active

### Error Handling

The GUI handles connection errors gracefully:
- Invalid connection strings show an error dialog
- Connection timeouts are caught and reported
- SSH authentication failures are displayed clearly
- The GUI never crashes from connection errors

## Requirements

For remote connections to work:
- SSH client must be installed (automatically installed by install.sh)
- SSH key-based authentication should be configured
- Remote Docker daemon must be running
- User must be in the docker group on the remote server

See [REMOTE_DOCKER.md](REMOTE_DOCKER.md) for detailed setup instructions.

## Troubleshooting

### Connection Button Does Nothing

- Ensure the config module is imported
- Check for errors in the console output

### Remote Hosts Not Appearing

- Verify the config file exists: `~/.config/docker_helper/config.yml`
- Check file permissions
- Try adding a host via CLI to test

### Connection Fails

- Verify SSH access: `ssh user@host`
- Check Docker is running on remote: `ssh user@host "docker ps"`
- Verify user is in docker group on remote
- Check connection string format

### GUI Doesn't Refresh After Connecting

- Check for errors in the terminal
- Restart the GUI
- Verify Docker client has permissions

## Future Enhancements

Potential improvements for future versions:
- Connection history/recent connections
- Test connection button before saving
- SSH key selection in the GUI
- Connection status indicator (green/red dot)
- Save custom connections option
- Import/export connection configurations
- Connection profiles with different defaults
- Automatic reconnection on connection loss
