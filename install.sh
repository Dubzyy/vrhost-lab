#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Starting VRHost Lab installation..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_DIR="/opt/vrhost-lab"

# Check KVM support
print_status "Checking KVM virtualization support..."
if ! grep -E -q 'vmx|svm' /proc/cpuinfo; then
    print_error "CPU does not support virtualization (VT-x/AMD-V)"
    print_error "Enable virtualization in BIOS or use a bare metal server"
    exit 1
fi
print_success "KVM support detected"

# Update package list
print_status "Updating package list..."
apt-get update -qq

# Install Node.js 20.x
print_status "Installing Node.js 20.x..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    print_success "Node.js $(node --version) installed"
else
    print_success "Node.js $(node --version) already installed"
fi

# Install Python 3.11+
print_status "Installing Python 3.11+..."
apt-get install -y python3 python3-pip python3-venv
print_success "Python $(python3 --version) installed"

# Install KVM and virtualization tools
print_status "Installing KVM, QEMU, and libvirt..."
apt-get install -y \
    qemu-kvm \
    libvirt-daemon-system \
    libvirt-clients \
    bridge-utils \
    virt-manager \
    virtinst \
    libguestfs-tools \
    guestfs-tools

# Add current user to libvirt groups (if not root)
if [ -n "$SUDO_USER" ]; then
    usermod -aG libvirt,kvm "$SUDO_USER"
    print_success "Added $SUDO_USER to libvirt and kvm groups"
fi

# Start and enable libvirtd
systemctl enable --now libvirtd
print_success "libvirtd service started and enabled"

# Install ttyd for web console
print_status "Installing ttyd..."
if ! command -v ttyd &> /dev/null; then
    TTYD_VERSION="1.7.3"
    wget -q "https://github.com/tsl0922/ttyd/releases/download/${TTYD_VERSION}/ttyd.x86_64" -O /usr/local/bin/ttyd
    chmod +x /usr/local/bin/ttyd
    print_success "ttyd ${TTYD_VERSION} installed"
else
    print_success "ttyd already installed"
fi

# Copy project to /opt if not already there
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    print_status "Copying project to ${INSTALL_DIR}..."
    mkdir -p "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    print_success "Project copied to ${INSTALL_DIR}"
else
    print_success "Already running from ${INSTALL_DIR}"
fi

cd "$INSTALL_DIR"

# Install automation scripts
print_status "Installing automation scripts..."
if [ -d "$INSTALL_DIR/scripts" ]; then
    # Install mkjuniper (vSRX routers)
    if [ -f "$INSTALL_DIR/scripts/mkjuniper" ]; then
        cp "$INSTALL_DIR/scripts/mkjuniper" /usr/local/bin/
        chmod +x /usr/local/bin/mkjuniper
        print_success "mkjuniper script installed"
    else
        print_warning "mkjuniper script not found in scripts/ directory"
    fi

    # Install mkcsr1000v (Cisco routers)
    if [ -f "$INSTALL_DIR/scripts/mkcsr1000v" ]; then
        cp "$INSTALL_DIR/scripts/mkcsr1000v" /usr/local/bin/
        chmod +x /usr/local/bin/mkcsr1000v
        print_success "mkcsr1000v script installed"
    else
        print_warning "mkcsr1000v script not found in scripts/ directory"
    fi

    # Install mkviosl2 (Cisco IOSvL2 switches)
    if [ -f "$INSTALL_DIR/scripts/mkviosl2" ]; then
        cp "$INSTALL_DIR/scripts/mkviosl2" /usr/local/bin/
        chmod +x /usr/local/bin/mkviosl2
        print_success "mkviosl2 script installed"
    else
        print_warning "mkviosl2 script not found in scripts/ directory"
    fi

    # Install mkvqfx (Juniper vQFX switches)
    if [ -f "$INSTALL_DIR/scripts/mkvqfx" ]; then
        cp "$INSTALL_DIR/scripts/mkvqfx" /usr/local/bin/
        chmod +x /usr/local/bin/mkvqfx
        print_success "mkvqfx script installed"
    else
        print_warning "mkvqfx-delete script not found in scripts/ directory"
    fi

    # Install mkvqfx-delete (vQFX cleanup)
    if [ -f "$INSTALL_DIR/scripts/mkvqfx-delete" ]; then
        cp "$INSTALL_DIR/scripts/mkvqfx-delete" /usr/local/bin/
        chmod +x /usr/local/bin/mkvqfx-delete
        print_success "mkvqfx-delete script installed"
    else
        print_warning "mkvqfx-delete script not found in scripts/ directory"
    fi

    # Install mkvm (generic)
    if [ -f "$INSTALL_DIR/scripts/mkvm" ]; then
        cp "$INSTALL_DIR/scripts/mkvm" /usr/local/bin/
        chmod +x /usr/local/bin/mkvm
        print_success "mkvm script installed"
    fi
else
    print_warning "scripts/ directory not found - automation scripts not installed"
fi

# Setup Python virtual environment for backend
print_status "Setting up Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r backend/requirements.txt
deactivate
print_success "Python backend dependencies installed"

# Build React frontend
print_status "Building React frontend..."
cd "$INSTALL_DIR/frontend"
npm install --quiet
npm run build
print_success "React frontend built"

# Create systemd service for backend API
print_status "Creating systemd service for backend API..."
cat > /etc/systemd/system/vrhost-api.service << 'APIEOF'
[Unit]
Description=VRHost Lab API Service
After=network.target libvirtd.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vrhost-lab/backend
Environment="PATH=/opt/vrhost-lab/venv/bin"
ExecStart=/opt/vrhost-lab/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
APIEOF

# Create systemd service for frontend web server
print_status "Creating systemd service for frontend web server..."
cat > /etc/systemd/system/vrhost-web.service << 'WEBEOF'
[Unit]
Description=VRHost Lab Web Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vrhost-lab/frontend
ExecStart=/usr/bin/npx serve -s build -l 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
WEBEOF

# Reload systemd and enable services
print_status "Enabling and starting services..."
systemctl daemon-reload
systemctl enable vrhost-api vrhost-web
systemctl restart vrhost-api vrhost-web

# Wait a moment for services to start
sleep 3

# Check service status
if systemctl is-active --quiet vrhost-api; then
    print_success "vrhost-api service is running"
else
    print_error "vrhost-api service failed to start"
    systemctl status vrhost-api --no-pager
fi

if systemctl is-active --quiet vrhost-web; then
    print_success "vrhost-web service is running"
else
    print_error "vrhost-web service failed to start"
    systemctl status vrhost-web --no-pager
fi

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

# Print completion message
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  VRHost Lab Installation Complete! 🚀${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}Access Points:${NC}"
echo -e "  Web Interface: ${GREEN}http://localhost:3000${NC}"
echo -e "  Web Interface: ${GREEN}http://${SERVER_IP}:3000${NC}"
echo -e "  API Docs:      ${GREEN}http://${SERVER_IP}:8000/docs${NC}"
echo ""
echo -e "${BLUE}Installed Scripts:${NC}"
echo -e "  ${GREEN}mkjuniper${NC}      - Create Juniper vSRX router"
echo -e "  ${GREEN}mkcsr1000v${NC}     - Create Cisco CSR1000v router"
echo -e "  ${GREEN}mkviosl2${NC}       - Create Cisco IOSvL2 switch"
echo -e "  ${GREEN}mkvqfx${NC}         - Create Juniper vQFX switch"
echo -e "  ${GREEN}mkvqfx-delete${NC}  - Delete Juniper vQFX switch"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Add router/switch images to /var/lib/libvirt/images/"
echo -e "     - Juniper vSRX:  /var/lib/libvirt/images/juniper/"
echo -e "     - Juniper vQFX:  /var/lib/libvirt/images/juniper/"
echo -e "     - Cisco routers: /var/lib/libvirt/images/cisco/"
echo -e "     - Cisco switches: /var/lib/libvirt/images/cisco/"
echo -e "  2. Update image paths in scripts if needed:"
echo -e "     - ${GREEN}sudo nano /usr/local/bin/mkjuniper${NC}"
echo -e "     - ${GREEN}sudo nano /usr/local/bin/mkcsr1000v${NC}"
echo -e "     - ${GREEN}sudo nano /usr/local/bin/mkviosl2${NC}"
echo -e "     - ${GREEN}sudo nano /usr/local/bin/mkvqfx${NC}"
echo -e "  3. Create your first device:"
echo -e "     - ${GREEN}sudo mkjuniper r1 10.10.50.10${NC}  (Juniper vSRX router)"
echo -e "     - ${GREEN}sudo mkcsr1000v csr1${NC}           (Cisco CSR1000v router)"
echo -e "     - ${GREEN}sudo mkviosl2 sw1${NC}              (Cisco IOSvL2 switch)"
echo -e "     - ${GREEN}sudo mkvqfx sw2${NC}                (Juniper vQFX switch)"
echo ""
echo -e "${BLUE}Device Support:${NC}"
echo -e "  Routers:  ${GREEN}Juniper vSRX • Cisco CSR1000v${NC}"
echo -e "  Switches: ${GREEN}Cisco IOSvL2 • Juniper vQFX${NC}"
echo ""
echo -e "${BLUE}Service Management:${NC}"
echo -e "  Status:  ${GREEN}sudo systemctl status vrhost-api vrhost-web${NC}"
echo -e "  Restart: ${GREEN}sudo systemctl restart vrhost-api vrhost-web${NC}"
echo -e "  Logs:    ${GREEN}sudo journalctl -u vrhost-api -f${NC}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  README:  ${GREEN}cat /opt/vrhost-lab/README.md${NC}"
echo -e "  Scripts: ${GREEN}cat /opt/vrhost-lab/scripts/README.md${NC}"
echo ""
echo -e "${GREEN}Happy Labbing! 🎉${NC}"
echo ""
