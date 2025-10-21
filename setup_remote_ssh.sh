#!/bin/bash
#
# SSH Key Setup Helper for Docker Remote Connections
# This script helps you set up SSH key authentication for remote Docker hosts
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "  Docker Remote SSH Setup Helper"
echo "=========================================="
echo

# Get remote host details
read -p "Enter remote hostname or IP: " REMOTE_HOST
read -p "Enter SSH username: " REMOTE_USER
read -p "Enter SSH port (default: 22): " SSH_PORT
SSH_PORT=${SSH_PORT:-22}

echo
log_info "Configuration:"
log_info "  Host: $REMOTE_HOST"
log_info "  User: $REMOTE_USER"
log_info "  Port: $SSH_PORT"
echo

# Check if SSH key exists
if [ ! -f ~/.ssh/id_ed25519 ] && [ ! -f ~/.ssh/id_rsa ]; then
    log_warning "No SSH key found. Let's create one!"
    echo
    read -p "Create a new SSH key? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        log_info "Generating ED25519 SSH key..."
        ssh-keygen -t ed25519 -C "$USER@$(hostname)-docker-remote"
        log_success "SSH key generated!"
    else
        log_error "SSH key is required for remote Docker connections."
        exit 1
    fi
fi

# Determine which key to use
if [ -f ~/.ssh/id_ed25519 ]; then
    SSH_KEY=~/.ssh/id_ed25519
    SSH_KEY_PUB=~/.ssh/id_ed25519.pub
elif [ -f ~/.ssh/id_rsa ]; then
    SSH_KEY=~/.ssh/id_rsa
    SSH_KEY_PUB=~/.ssh/id_rsa.pub
fi

log_info "Using SSH key: $SSH_KEY"
echo

# Test SSH connection
log_info "Testing SSH connection..."
if ssh -p $SSH_PORT -o BatchMode=yes -o ConnectTimeout=5 $REMOTE_USER@$REMOTE_HOST exit 2>/dev/null; then
    log_success "SSH key authentication is already working!"
else
    log_warning "SSH key authentication not set up yet."
    echo
    log_info "We need to copy your SSH key to the remote server."
    log_info "You will be prompted for your password on the remote server."
    echo
    read -p "Copy SSH key to remote server? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if command -v ssh-copy-id &> /dev/null; then
            log_info "Copying SSH key to $REMOTE_USER@$REMOTE_HOST..."
            ssh-copy-id -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST
        else
            log_info "ssh-copy-id not found, using manual method..."
            cat $SSH_KEY_PUB | ssh -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
        fi

        # Test again
        log_info "Testing SSH connection again..."
        if ssh -p $SSH_PORT -o BatchMode=yes -o ConnectTimeout=5 $REMOTE_USER@$REMOTE_HOST exit 2>/dev/null; then
            log_success "SSH key authentication is now working!"
        else
            log_error "SSH key authentication still not working. Please check your SSH configuration."
            exit 1
        fi
    else
        log_error "Cannot proceed without SSH key authentication."
        exit 1
    fi
fi

echo

# Check if Docker is installed on remote
log_info "Checking if Docker is installed on remote server..."
if ! ssh -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST "command -v docker" &>/dev/null; then
    log_error "Docker is not installed on the remote server!"
    echo
    read -p "Would you like to see the install command? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo
        log_info "You can install Docker on the remote server by running:"
        echo "  scp install.sh $REMOTE_USER@$REMOTE_HOST:~/"
        echo "  ssh -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST 'bash ~/install.sh'"
    fi
    exit 1
fi

log_success "Docker is installed on remote server"

# Check if user is in docker group
log_info "Checking if user is in docker group on remote server..."
if ! ssh -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST "groups | grep -q docker"; then
    log_warning "User $REMOTE_USER is not in the docker group on remote server"
    echo
    log_info "To add the user to docker group, run on the remote server:"
    echo "  sudo usermod -aG docker $REMOTE_USER"
    echo "  Then log out and log back in"
    echo
    read -p "Try to add user to docker group now? (requires sudo on remote) (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Adding user to docker group..."
        ssh -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST "sudo usermod -aG docker $REMOTE_USER"
        log_success "User added to docker group"
        log_warning "You need to log out and back in on the remote server for this to take effect"
        echo
        read -p "Press Enter after logging out and back in on remote server..."
    else
        log_warning "You will need to add the user to docker group manually"
        exit 1
    fi
fi

log_success "User is in docker group on remote server"

# Test Docker access
log_info "Testing Docker access on remote server..."
if ssh -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST "docker ps" &>/dev/null; then
    log_success "Docker access works on remote server!"
else
    log_error "Cannot access Docker on remote server"
    log_info "This usually means:"
    log_info "  1. User is not in docker group (and hasn't logged out/in yet)"
    log_info "  2. Docker daemon is not running"
    log_info "  3. Permission issues with Docker socket"
    exit 1
fi

echo

# Test Docker connection from local
log_info "Testing Docker remote connection..."
CONNECTION_STRING="ssh://$REMOTE_USER@$REMOTE_HOST"
if [ "$SSH_PORT" != "22" ]; then
    CONNECTION_STRING="ssh://$REMOTE_USER@$REMOTE_HOST:$SSH_PORT"
fi

log_info "Connection string: $CONNECTION_STRING"

# Create a test Python script
cat > /tmp/test_docker_connection.py << 'EOF'
import sys
import docker

docker_host = sys.argv[1]
try:
    client = docker.DockerClient(base_url=docker_host)
    client.ping()
    print(f"✓ Successfully connected to {docker_host}")
    info = client.info()
    print(f"  Docker version: {info['ServerVersion']}")
    print(f"  Containers: {info['Containers']} ({info['ContainersRunning']} running)")
    print(f"  Images: {info['Images']}")
    sys.exit(0)
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)
EOF

if python3 /tmp/test_docker_connection.py "$CONNECTION_STRING" 2>/dev/null; then
    log_success "Remote Docker connection is working!"
else
    log_error "Remote Docker connection failed"
    echo
    log_info "Troubleshooting steps:"
    log_info "  1. Make sure SSH works: ssh -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST"
    log_info "  2. Check Docker on remote: ssh -p $SSH_PORT $REMOTE_USER@$REMOTE_HOST 'docker ps'"
    log_info "  3. Verify Python docker package: pip3 install --user docker"
    exit 1
fi

rm /tmp/test_docker_connection.py

echo
echo "=========================================="
log_success "Setup completed successfully!"
echo "=========================================="
echo
log_info "You can now add this remote host to docker_helper:"
echo
if [ "$SSH_PORT" = "22" ]; then
    echo "  python3 main.py remote add myserver $REMOTE_HOST --user $REMOTE_USER"
else
    echo "  python3 main.py remote add myserver $REMOTE_HOST --user $REMOTE_USER --port $SSH_PORT"
fi
echo
log_info "Or use it directly:"
echo "  python3 main.py --host $CONNECTION_STRING status"
echo "  python3 main.py --gui --host $CONNECTION_STRING"
echo
