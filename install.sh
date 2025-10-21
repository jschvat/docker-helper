#!/bin/bash
#
# Docker Helper Interactive Installation Script
# Installs Docker CE, dependencies, and docker_helper across multiple Linux distributions
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "Please do not run this script as root. Run as a regular user with sudo privileges."
        exit 1
    fi

    # Check if user has sudo privileges
    if ! sudo -v &> /dev/null; then
        log_error "This script requires sudo privileges. Please ensure your user has sudo access."
        exit 1
    fi
}

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
        DISTRO_NAME=$NAME
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
        DISTRO_NAME=$(cat /etc/redhat-release)
    else
        log_error "Unable to detect Linux distribution"
        exit 1
    fi

    log_info "Detected distribution: $DISTRO_NAME"
}

# Check if Docker is already installed
check_docker_installed() {
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        log_warning "Docker is already installed: $DOCKER_VERSION"
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled."
            exit 0
        fi
    fi
}

# Install Docker on Ubuntu/Debian
install_docker_debian() {
    log_info "Installing Docker CE on Debian-based system..."

    # Remove old versions
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # Update package index
    sudo apt-get update

    # Install dependencies
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    log_success "Docker CE installed successfully on Debian-based system"
}

# Install Docker on Fedora
install_docker_fedora() {
    log_info "Installing Docker CE on Fedora..."

    # Remove old versions
    sudo dnf remove -y docker \
                    docker-client \
                    docker-client-latest \
                    docker-common \
                    docker-latest \
                    docker-latest-logrotate \
                    docker-logrotate \
                    docker-selinux \
                    docker-engine-selinux \
                    docker-engine 2>/dev/null || true

    # Install dnf-plugins-core
    sudo dnf -y install dnf-plugins-core

    # Set up the repository
    sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

    # Install Docker Engine
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    log_success "Docker CE installed successfully on Fedora"
}

# Install Docker on CentOS/RHEL
install_docker_rhel() {
    log_info "Installing Docker CE on RHEL/CentOS..."

    # Remove old versions
    sudo yum remove -y docker \
                    docker-client \
                    docker-client-latest \
                    docker-common \
                    docker-latest \
                    docker-latest-logrotate \
                    docker-logrotate \
                    docker-engine 2>/dev/null || true

    # Install yum-utils
    sudo yum install -y yum-utils

    # Set up the repository
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

    # Install Docker Engine
    sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    log_success "Docker CE installed successfully on RHEL/CentOS"
}

# Install Docker on Arch Linux
install_docker_arch() {
    log_info "Installing Docker on Arch Linux..."

    # Update package database
    sudo pacman -Sy

    # Install Docker
    sudo pacman -S --noconfirm docker docker-compose

    log_success "Docker installed successfully on Arch Linux"
}

# Install Docker on openSUSE
install_docker_opensuse() {
    log_info "Installing Docker on openSUSE..."

    # Remove old versions
    sudo zypper remove -y docker 2>/dev/null || true

    # Add Docker repository
    sudo zypper addrepo https://download.docker.com/linux/sles/docker-ce.repo

    # Install Docker
    sudo zypper install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    log_success "Docker installed successfully on openSUSE"
}

# Main Docker installation dispatcher
install_docker() {
    case "$OS" in
        ubuntu|debian|linuxmint|pop)
            install_docker_debian
            ;;
        fedora)
            install_docker_fedora
            ;;
        centos|rhel|rocky|almalinux)
            install_docker_rhel
            ;;
        arch|manjaro)
            install_docker_arch
            ;;
        opensuse|opensuse-leap|opensuse-tumbleweed|sles)
            install_docker_opensuse
            ;;
        *)
            log_error "Unsupported distribution: $OS"
            log_info "Supported distributions: Ubuntu, Debian, Fedora, CentOS, RHEL, Arch, openSUSE"
            exit 1
            ;;
    esac
}

# Setup Docker group and add user
setup_docker_group() {
    log_info "Setting up Docker group..."

    # Create docker group if it doesn't exist
    if ! getent group docker > /dev/null 2>&1; then
        sudo groupadd docker
        log_success "Docker group created"
    else
        log_info "Docker group already exists"
    fi

    # Add current user to docker group
    if ! groups $USER | grep -q '\bdocker\b'; then
        sudo usermod -aG docker $USER
        log_success "User $USER added to docker group"
        log_warning "You will need to log out and back in for group membership to take effect"
    else
        log_info "User $USER is already in docker group"
    fi
}

# Start and enable Docker service
enable_docker_service() {
    log_info "Starting and enabling Docker service..."

    sudo systemctl start docker
    sudo systemctl enable docker

    log_success "Docker service started and enabled"
}

# Install Python and dependencies (including SSH support for remote Docker)
install_python_deps() {
    log_info "Installing Python and dependencies..."

    case "$OS" in
        ubuntu|debian|linuxmint|pop)
            sudo apt-get install -y python3 python3-pip python3-venv \
                python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
                libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev \
                openssh-client
            ;;
        fedora)
            sudo dnf install -y python3 python3-pip \
                python3-gobject gtk3 cairo-gobject-devel gobject-introspection-devel \
                gcc pkg-config python3-devel cairo-devel \
                openssh-clients
            ;;
        centos|rhel|rocky|almalinux)
            sudo yum install -y python3 python3-pip \
                python3-gobject gtk3 cairo-gobject-devel gobject-introspection-devel \
                gcc pkg-config python3-devel cairo-devel \
                openssh-clients
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm python python-pip python-gobject gtk3 cairo gobject-introspection \
                openssh
            ;;
        opensuse|opensuse-leap|opensuse-tumbleweed|sles)
            sudo zypper install -y python3 python3-pip \
                python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-3_0 \
                gobject-introspection-devel gcc pkg-config python3-devel cairo-devel \
                openssh
            ;;
    esac

    log_success "Python and system dependencies installed (including SSH client for remote Docker)"
}

# Install docker_helper
install_docker_helper() {
    log_info "Installing docker_helper..."

    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    # Check if requirements.txt exists
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_error "requirements.txt not found in $SCRIPT_DIR"
        exit 1
    fi

    # Create virtual environment (optional but recommended)
    read -p "Do you want to install docker_helper in a virtual environment? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$SCRIPT_DIR/venv"
        source "$SCRIPT_DIR/venv/bin/activate"
        log_success "Virtual environment created and activated"

        # Upgrade pip
        pip install --upgrade pip

        # Install requirements
        log_info "Installing Python requirements..."
        pip install -r "$SCRIPT_DIR/requirements.txt"

        log_success "docker_helper installed in virtual environment"
        log_info "To use docker_helper, activate the virtual environment first:"
        log_info "  source $SCRIPT_DIR/venv/bin/activate"
        log_info "  python main.py --help"
    else
        # Install system-wide (requires sudo for some packages)
        log_info "Installing Python requirements system-wide..."
        pip3 install --user -r "$SCRIPT_DIR/requirements.txt"

        log_success "docker_helper installed system-wide"
        log_info "You can now run docker_helper with:"
        log_info "  python3 $SCRIPT_DIR/main.py --help"
    fi

    # Make main.py executable
    chmod +x "$SCRIPT_DIR/main.py" 2>/dev/null || true

    # Optionally create a symlink or alias
    read -p "Do you want to create a symlink to /usr/local/bin/docker-helper? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "$SCRIPT_DIR/venv" ]; then
            # Create wrapper script for venv
            cat > /tmp/docker-helper << EOF
#!/bin/bash
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/main.py" "\$@"
EOF
            sudo mv /tmp/docker-helper /usr/local/bin/docker-helper
            sudo chmod +x /usr/local/bin/docker-helper
        else
            sudo ln -sf "$SCRIPT_DIR/main.py" /usr/local/bin/docker-helper
        fi
        log_success "Symlink created: /usr/local/bin/docker-helper"
    fi
}

# Test Docker installation
test_docker() {
    log_info "Testing Docker installation..."

    # Try to run without sudo first (may not work until relogin)
    if docker run --rm hello-world &> /dev/null; then
        log_success "Docker is working correctly without sudo!"
    else
        log_info "Testing with sudo (you may need to log out and back in to use Docker without sudo)..."
        if sudo docker run --rm hello-world &> /dev/null; then
            log_success "Docker is working correctly with sudo"
            log_warning "Remember to log out and back in to use Docker without sudo"
        else
            log_error "Docker test failed. Please check the installation."
            return 1
        fi
    fi
}

# Main installation flow
main() {
    echo "========================================"
    echo "  Docker Helper Installation Script"
    echo "========================================"
    echo

    check_root
    detect_distro

    echo
    log_info "This script will:"
    log_info "  1. Install Docker CE"
    log_info "  2. Setup docker group and add your user"
    log_info "  3. Install Python dependencies"
    log_info "  4. Install docker_helper application"
    echo

    read -p "Do you want to continue? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "Installation cancelled."
        exit 0
    fi

    echo
    check_docker_installed

    echo
    log_info "Step 1/6: Installing Docker CE..."
    install_docker

    echo
    log_info "Step 2/6: Setting up Docker group..."
    setup_docker_group

    echo
    log_info "Step 3/6: Starting Docker service..."
    enable_docker_service

    echo
    log_info "Step 4/6: Testing Docker installation..."
    test_docker

    echo
    log_info "Step 5/6: Installing Python dependencies..."
    install_python_deps

    echo
    log_info "Step 6/6: Installing docker_helper..."
    install_docker_helper

    echo
    echo "========================================"
    log_success "Installation completed successfully!"
    echo "========================================"
    echo
    log_warning "IMPORTANT: You must log out and log back in for Docker group changes to take effect."
    log_info "After logging back in, you can use Docker without sudo."
    echo
    log_info "Docker version: $(docker --version)"
    log_info "Docker Compose version: $(docker compose version)"
    echo
    log_info "To get started with docker_helper:"
    log_info "  python3 main.py --help"
    log_info "  python3 main.py --gui  (for GUI interface)"
    echo
}

# Run main function
main
