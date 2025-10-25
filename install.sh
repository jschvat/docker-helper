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
            sudo apt-get install -y \
                python3 python3-pip python3-venv \
                python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
                libgirepository1.0-dev libcairo2-dev \
                gcc g++ pkg-config python3-dev \
                gir1.2-vte-2.91 libvte-2.91-dev \
                gir1.2-gdkpixbuf-2.0 libgdk-pixbuf2.0-dev \
                gir1.2-pango-1.0 libpango1.0-dev \
                openssh-client
            ;;
        fedora)
            sudo dnf install -y \
                python3 python3-pip python3-devel \
                python3-gobject gtk3 gtk3-devel \
                cairo-gobject-devel cairo-devel \
                gobject-introspection-devel \
                gcc gcc-c++ pkg-config \
                vte291 vte291-devel \
                gdk-pixbuf2 gdk-pixbuf2-devel \
                pango pango-devel \
                openssh-clients
            ;;
        centos|rhel|rocky|almalinux)
            sudo yum install -y \
                python3 python3-pip python3-devel \
                python3-gobject gtk3 gtk3-devel \
                cairo-gobject-devel cairo-devel \
                gobject-introspection-devel \
                gcc gcc-c++ pkg-config \
                vte291 vte291-devel \
                gdk-pixbuf2 gdk-pixbuf2-devel \
                pango pango-devel \
                openssh-clients
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm \
                python python-pip \
                python-gobject gtk3 \
                cairo gobject-introspection \
                gcc pkg-config \
                vte3 gdk-pixbuf2 pango \
                openssh
            ;;
        opensuse|opensuse-leap|opensuse-tumbleweed|sles)
            sudo zypper install -y \
                python3 python3-pip python3-devel \
                python3-gobject python3-gobject-Gdk \
                typelib-1_0-Gtk-3_0 gtk3-devel \
                gobject-introspection-devel \
                gcc gcc-c++ pkg-config \
                cairo-devel \
                typelib-1_0-Vte-2_91 vte-devel \
                typelib-1_0-GdkPixbuf-2_0 gdk-pixbuf-devel \
                typelib-1_0-Pango-1_0 pango-devel \
                openssh
            ;;
    esac

    log_success "Python and system dependencies installed (including all PyGObject requirements)"
}

# Install docker_helper
install_docker_helper() {
    log_info "Installing docker_helper to /opt/docker-helper..."

    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    INSTALL_DIR="/opt/docker-helper"

    # Check if requirements.txt exists
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_error "requirements.txt not found in $SCRIPT_DIR"
        exit 1
    fi

    # Create installation directory
    sudo mkdir -p "$INSTALL_DIR"

    # Copy all files to installation directory
    log_info "Copying files to $INSTALL_DIR..."
    sudo cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

    # Set ownership
    sudo chown -R root:root "$INSTALL_DIR"

    # Install Python dependencies system-wide
    log_info "Installing Python requirements..."
    sudo pip3 install -r "$INSTALL_DIR/requirements.txt"

    log_success "docker_helper files installed to $INSTALL_DIR"

    # Create wrapper script in /usr/local/bin
    log_info "Creating command-line wrapper..."
    sudo cat > /usr/local/bin/docker-helper << 'EOF'
#!/bin/bash
# Docker Helper command-line wrapper
exec python3 /opt/docker-helper/main.py "$@"
EOF
    sudo chmod +x /usr/local/bin/docker-helper

    log_success "Command-line tool installed: docker-helper"

    # Create desktop entry for GUI
    log_info "Creating desktop launcher..."
    sudo cat > /usr/share/applications/docker-helper.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Docker Helper
Comment=Docker Container Management Tool
Exec=/usr/local/bin/docker-helper --gui
Icon=docker
Terminal=false
Categories=System;Utility;
Keywords=docker;container;management;
StartupNotify=true
EOF

    log_success "Desktop launcher created"

    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        sudo update-desktop-database /usr/share/applications 2>/dev/null || true
    fi

    log_info "Installation complete!"
    log_info "You can run docker-helper from:"
    log_info "  - Command line: docker-helper --help"
    log_info "  - GUI: docker-helper --gui (or from your applications menu)"
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
    log_info "Docker Helper has been installed to: /opt/docker-helper"
    echo
    log_info "To get started with docker_helper:"
    log_info "  Command line: docker-helper --help"
    log_info "  GUI: docker-helper --gui"
    log_info "  Or find 'Docker Helper' in your applications menu"
    echo
    log_info "Available services: $(ls /opt/docker-helper/services/*.yml 2>/dev/null | wc -l) service configurations"
    echo
}

# Run main function
main
