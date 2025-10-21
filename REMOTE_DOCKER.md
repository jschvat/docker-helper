# Remote Docker Connection Guide

This guide explains how to connect `docker_helper` to remote Docker instances via SSH.

## Table of Contents

- [Prerequisites](#prerequisites)
- [SSH Key Setup](#ssh-key-setup)
- [Remote Docker Configuration](#remote-docker-configuration)
- [Using Remote Connections](#using-remote-connections)
- [Managing Remote Hosts](#managing-remote-hosts)
- [Troubleshooting](#troubleshooting)

## Prerequisites

1. **SSH access** to the remote server
2. **Docker installed** on the remote server
3. **SSH client** installed locally (installed automatically by install.sh)
4. **SSH key-based authentication** configured (recommended)

## SSH Key Setup

### 1. Generate SSH Key (if you don't have one)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Or for RSA:
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

Press Enter to accept the default file location (`~/.ssh/id_ed25519` or `~/.ssh/id_rsa`).

### 2. Copy SSH Key to Remote Server

```bash
ssh-copy-id user@remote-host
```

Or manually:

```bash
cat ~/.ssh/id_ed25519.pub | ssh user@remote-host "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 3. Test SSH Connection

```bash
ssh user@remote-host
```

If you can connect without entering a password, SSH key authentication is working.

## Remote Docker Configuration

### On the Remote Server

Ensure your user is in the `docker` group on the remote server:

```bash
# On the remote server
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

Verify Docker is running:

```bash
# On the remote server
sudo systemctl status docker
sudo systemctl start docker  # if not running
sudo systemctl enable docker # to start on boot
```

### Test Docker Access

```bash
# On the remote server
docker ps
# Should work without sudo
```

## Using Remote Connections

### Method 1: Direct Connection String

Connect to a remote Docker host using the `--host` or `-H` flag:

```bash
# Using SSH (default port 22)
python3 main.py --host ssh://user@remote-host status

# Using SSH with custom port
python3 main.py --host ssh://user@remote-host:2222 status

# Using TCP (not recommended without TLS)
python3 main.py --host tcp://remote-host:2375 status
```

### Method 2: Saved Remote Hosts

Add a remote host with a friendly name:

```bash
# Add a remote host
python3 main.py remote add production 192.168.1.100 --user john --description "Production Docker Server"

# Add with custom SSH port
python3 main.py remote add staging 192.168.1.101 --user john --port 2222 --description "Staging Server"

# List all saved remote hosts
python3 main.py remote list

# Use a saved remote host by name
python3 main.py --host production status

# Set a default remote host
python3 main.py remote set-default production

# Now you can use commands without --host flag
python3 main.py status

# Set back to local
python3 main.py remote set-default
```

### Method 3: GUI with Remote Host

Launch the GUI connected to a remote host:

```bash
# Connect to remote host
python3 main.py --gui --host ssh://user@remote-host

# Or use saved remote name
python3 main.py --gui --host production
```

The GUI header will show which host you're connected to.

## Managing Remote Hosts

### Add Remote Host

```bash
python3 main.py remote add <name> <host> [options]

Options:
  --user USER          SSH username (default: current user)
  --port PORT          SSH port (default: 22)
  --description DESC   Optional description
```

Example:
```bash
python3 main.py remote add homelab 192.168.1.50 --user docker --description "Home Lab Server"
```

### List Remote Hosts

```bash
python3 main.py remote list
```

Output:
```
Configured remote hosts:

  production:
    Host: 192.168.1.100
    User: john
    Port: 22
    Connection: ssh://john@192.168.1.100
    Description: Production Docker Server

  staging:
    Host: 192.168.1.101
    User: john
    Port: 2222
    Connection: ssh://john@192.168.1.101:2222
    Description: Staging Server
```

### Remove Remote Host

```bash
python3 main.py remote remove <name>
```

Example:
```bash
python3 main.py remote remove staging
```

### Set Default Host

Set a remote host as the default (used when no --host is specified):

```bash
# Set a saved remote as default
python3 main.py remote set-default production

# Reset to local Docker
python3 main.py remote set-default
```

## Configuration File

Remote host configurations are stored in `~/.config/docker_helper/config.yml`:

```yaml
default_host: production
remote_hosts:
  production:
    host: 192.168.1.100
    port: 22
    user: john
    docker_host: ssh://john@192.168.1.100
    description: Production Docker Server
  homelab:
    host: 192.168.1.50
    port: 22
    user: docker
    docker_host: ssh://docker@192.168.1.50
    description: Home Lab Server
```

## Examples

### Deploy Service to Remote Host

```bash
# One-time connection
python3 main.py --host ssh://user@remote-host install nginx

# Using saved remote
python3 main.py --host production install nginx

# If production is set as default
python3 main.py install nginx
```

### Monitor Remote Containers

```bash
# Check status on remote host
python3 main.py --host production status

# Start service on remote host
python3 main.py --host production start nginx

# Use GUI to monitor remote host
python3 main.py --gui --host production
```

### Work Across Multiple Hosts

```bash
# Add multiple remote hosts
python3 main.py remote add dev 192.168.1.10 --user dev
python3 main.py remote add staging 192.168.1.20 --user staging
python3 main.py remote add production 192.168.1.30 --user prod

# Deploy to each environment
python3 main.py --host dev install myapp
python3 main.py --host staging install myapp
python3 main.py --host production install myapp

# Check status across all
python3 main.py --host dev status
python3 main.py --host staging status
python3 main.py --host production status
```

## Troubleshooting

### Connection Refused

**Problem:** `Error connecting to Docker at ssh://user@host`

**Solutions:**
1. Verify SSH connection works:
   ```bash
   ssh user@host
   ```

2. Check Docker is running on remote host:
   ```bash
   ssh user@host "docker ps"
   ```

3. Verify user is in docker group on remote:
   ```bash
   ssh user@host "groups"
   ```

### Permission Denied

**Problem:** Permission denied when connecting to Docker

**Solution:**
Add your user to the docker group on the remote server:
```bash
ssh user@host "sudo usermod -aG docker $USER"
# Then log out and back in to the remote server
```

### SSH Key Issues

**Problem:** SSH key authentication not working

**Solutions:**
1. Check SSH key permissions:
   ```bash
   chmod 600 ~/.ssh/id_ed25519
   chmod 644 ~/.ssh/id_ed25519.pub
   ```

2. Check authorized_keys on remote:
   ```bash
   ssh user@host "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
   ```

3. Test SSH with verbose output:
   ```bash
   ssh -v user@host
   ```

### Port Issues

**Problem:** Connection timeout or refused on custom port

**Solution:**
1. Verify SSH is listening on the correct port:
   ```bash
   ssh user@host -p 2222
   ```

2. Add the port to your remote host configuration:
   ```bash
   python3 main.py remote add myhost host.example.com --port 2222
   ```

### Docker Not Found on Remote

**Problem:** Docker command not found on remote

**Solution:**
Ensure Docker is installed on the remote server. You can use the install script:
```bash
scp install.sh user@remote-host:~/
ssh user@remote-host "bash ~/install.sh"
```

## Security Considerations

1. **Always use SSH key authentication** instead of passwords
2. **Protect your SSH private keys** with a passphrase
3. **Use ssh-agent** to avoid repeatedly entering passphrases
4. **Avoid using TCP connections** without TLS encryption
5. **Use firewalls** to restrict SSH access to trusted IPs
6. **Keep Docker and SSH up to date** on all systems
7. **Use non-standard SSH ports** to reduce brute-force attempts
8. **Enable SSH two-factor authentication** for production servers

## Advanced Configuration

### Using SSH Config

You can simplify SSH connections by adding entries to `~/.ssh/config`:

```
Host production
    HostName 192.168.1.100
    User john
    Port 22
    IdentityFile ~/.ssh/production_key

Host staging
    HostName 192.168.1.101
    User john
    Port 2222
    IdentityFile ~/.ssh/staging_key
```

Then use the alias in docker_helper:
```bash
python3 main.py --host ssh://production status
```

### SSH Agent Forwarding

To use your local SSH keys on the remote server:

```bash
# Add to ~/.ssh/config
Host production
    ForwardAgent yes
```

### SSH Tunneling

For additional security, you can use SSH tunneling:

```bash
# Create SSH tunnel
ssh -L 2375:localhost:2375 user@remote-host -N -f

# Connect via local tunnel
python3 main.py --host tcp://localhost:2375 status
```

## Connection String Formats

docker_helper supports these connection formats:

- `ssh://user@host` - SSH connection (port 22)
- `ssh://user@host:port` - SSH with custom port
- `tcp://host:port` - TCP connection (not recommended without TLS)
- `unix:///var/run/docker.sock` - Local Unix socket (default)
- `saved-name` - Use a saved remote host configuration

## Best Practices

1. **Use meaningful names** for saved remote hosts (e.g., "production", "staging", "dev")
2. **Add descriptions** to help identify each remote host
3. **Set appropriate defaults** based on your most common workflow
4. **Test connections** before deploying services
5. **Keep SSH keys secure** and use different keys for different environments
6. **Document your remote hosts** and their purposes
7. **Use SSH config** for complex SSH setups
8. **Monitor your remote Docker instances** regularly
