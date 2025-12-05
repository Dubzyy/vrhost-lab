#!/bin/bash

# VRHost Lab Installer
# One-command installation script for multi-vendor network lab platform

set -e

INSTALL_DIR="/opt/vrhost-lab"
API_PORT=8000
WEB_PORT=3000

echo "============================================"
echo "   VRHost Lab - Automated Installation"
echo "   Multi-Vendor Network Lab Platform"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "✓ Running as root"

# Check OS
if [ ! -f /etc/os-release ]; then
    echo "❌ Cannot detect OS. This installer supports Ubuntu/Debian."
    exit 1
fi

. /etc/os-release
if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
    echo "⚠️  Warning: This installer is designed for Ubuntu/Debian"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✓ OS: $PRETTY_NAME"

# Step 1: Install system dependencies
echo ""
echo "[1/9] Installing system dependencies..."
apt update -qq
apt install -y \
    libvirt-daemon-system \
    libvirt-clients \
    qemu-kvm \
    bridge-utils \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libvirt-dev \
    pkg-config \
    gcc \
    curl \
    git \
    ttyd > /dev/null 2>&1

echo "✓ System dependencies installed"

# Step 2: Install Node.js 20
echo ""
echo "[2/9] Installing Node.js 20..."
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'.' -f1 | sed 's/v//')" -lt 20 ]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1
    apt install -y nodejs > /dev/null 2>&1
fi
echo "✓ Node.js $(node -v) installed"

# Step 3: Verify KVM support
echo ""
echo "[3/9] Verifying KVM virtualization support..."
if ! grep -qE '(vmx|svm)' /proc/cpuinfo; then
    echo "⚠️  Warning: CPU virtualization extensions not detected"
    echo "   Make sure VT-x/AMD-V is enabled in BIOS"
fi
if [ -e /dev/kvm ]; then
    echo "✓ KVM support verified"
else
    echo "⚠️  Warning: /dev/kvm not found - KVM may not be available"
fi

# Step 4: Setup Python backend
echo ""
echo "[4/9] Setting up Python backend..."
cd "$INSTALL_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet \
    fastapi \
    uvicorn[standard] \
    libvirt-python \
    pydantic \
    websockets \
    python-multipart

echo "✓ Backend dependencies installed"

# Step 5: Install helper scripts
echo ""
echo "[5/9] Installing helper scripts..."

# Install mkjuniper
if [ -f "$INSTALL_DIR/scripts/mkjuniper" ]; then
    cp "$INSTALL_DIR/scripts/mkjuniper" /usr/local/bin/mkjuniper
    chmod +x /usr/local/bin/mkjuniper
    echo "✓ mkjuniper installed (Juniper vSRX)"
else
    echo "⚠️  mkjuniper script not found - you'll need to add it manually"
fi

# Install mkcsr1000v
if [ -f "$INSTALL_DIR/scripts/mkcsr1000v" ]; then
    cp "$INSTALL_DIR/scripts/mkcsr1000v" /usr/local/bin/mkcsr1000v
    chmod +x /usr/local/bin/mkcsr1000v
    echo "✓ mkcsr1000v installed (Cisco CSR1000v)"
else
    echo "⚠️  mkcsr1000v script not found - you'll need to add it manually"
fi

# Step 6: Setup React frontend
echo ""
echo "[6/9] Setting up React frontend..."
cd "$INSTALL_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install --silent > /dev/null 2>&1
fi
echo "✓ Frontend dependencies installed"

# Step 7: Build frontend for production
echo ""
echo "[7/9] Building frontend for production..."
cd "$INSTALL_DIR/frontend"
npm run build --silent > /dev/null 2>&1
npm install -g serve --silent > /dev/null 2>&1
echo "✓ Frontend built"

# Step 8: Create systemd services
echo ""
echo "[8/9] Creating systemd services..."

# Backend service
cat > /etc/systemd/system/vrhost-api.service <<APISERVICE
[Unit]
Description=VRHost Lab API Server
After=network.target libvirtd.service
Requires=libvirtd.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$INSTALL_DIR/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port $API_PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
APISERVICE

# Frontend service (production build)
cat > /etc/systemd/system/vrhost-web.service <<WEBSERVICE
[Unit]
Description=VRHost Lab Web Interface
After=network.target vrhost-api.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/frontend
Environment="PATH=/usr/bin:/bin"
ExecStart=/usr/bin/npx serve -s build -l tcp://0.0.0.0:$WEB_PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
WEBSERVICE

systemctl daemon-reload
echo "✓ Systemd services created"

# Step 9: Start services
echo ""
echo "[9/9] Starting services..."
systemctl enable vrhost-api > /dev/null 2>&1
systemctl enable vrhost-web > /dev/null 2>&1
systemctl start vrhost-api
systemctl start vrhost-web

# Wait for services to start
sleep 3

# Check service status
API_STATUS=$(systemctl is-active vrhost-api)
WEB_STATUS=$(systemctl is-active vrhost-web)

if [ "$API_STATUS" = "active" ] && [ "$WEB_STATUS" = "active" ]; then
    echo "✓ Services started and enabled"
else
    echo "⚠️  Warning: Some services may not have started properly"
    echo "   API Status: $API_STATUS"
    echo "   Web Status: $WEB_STATUS"
    echo "   Check logs with: journalctl -u vrhost-api -n 50"
fi

# Get server IP
SERVER_IP=$(ip route get 1.1.1.1 | grep -oP 'src \K[\d.]+' 2>/dev/null || hostname -I | awk '{print $1}')

echo ""
echo "============================================"
echo "   ✅ VRHost Lab Installation Complete!"
echo "============================================"
echo ""
echo "🌐 Access Points:"
echo "   Web Interface: http://$SERVER_IP:$WEB_PORT"
echo "   API Server:    http://$SERVER_IP:$API_PORT"
echo "   API Docs:      http://$SERVER_IP:$API_PORT/docs"
echo ""
echo "🚀 Supported Platforms:"
echo "   ✓ Juniper vSRX   (use: mkjuniper <name>)"
echo "   ✓ Cisco CSR1000v (use: mkcsr1000v <name>)"
echo ""
echo "⚠️  IMPORTANT - Next Steps:"
echo "   1. Add router images to /var/lib/libvirt/images/"
echo "      - Juniper: /var/lib/libvirt/images/juniper/vsrx3-*.qcow2"
echo "      - Cisco:   /var/lib/libvirt/images/cisco/csr1000v-*.qcow2"
echo ""
echo "   2. Update image paths in scripts:"
echo "      - Edit /usr/local/bin/mkjuniper (line 13)"
echo "      - Edit /usr/local/bin/mkcsr1000v (line 13)"
echo ""
echo "📊 Service Management:"
echo "   Status:  systemctl status vrhost-api vrhost-web"
echo "   Start:   systemctl start vrhost-api vrhost-web"
echo "   Stop:    systemctl stop vrhost-api vrhost-web"
echo "   Restart: systemctl restart vrhost-api vrhost-web"
echo ""
echo "📝 View Logs:"
echo "   API:     journalctl -u vrhost-api -f"
echo "   Web:     journalctl -u vrhost-web -f"
echo ""
echo "📚 Documentation:"
echo "   GitHub:  https://github.com/Dubzyy/vrhost-lab"
echo "   README:  $INSTALL_DIR/README.md"
echo ""
echo "🎉 Happy Lab Building!"
echo ""
