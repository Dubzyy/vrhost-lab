#!/bin/bash

# VRHost Lab Installer
# One-command installation script

set -e

INSTALL_DIR="/opt/vrhost-lab"
API_PORT=8000
WEB_PORT=3000

echo "============================================"
echo "   VRHost Lab - Automated Installation"
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
echo "[1/7] Installing system dependencies..."
apt update -qq
apt install -y \
    libvirt-daemon-system \
    libvirt-clients \
    qemu-kvm \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libvirt-dev \
    pkg-config \
    gcc \
    curl \
    git > /dev/null 2>&1

echo "✓ System dependencies installed"

# Step 2: Install Node.js 20
echo ""
echo "[2/7] Installing Node.js 20..."
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'.' -f1 | sed 's/v//')" -lt 20 ]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1
    apt install -y nodejs > /dev/null 2>&1
fi
echo "✓ Node.js $(node -v) installed"

# Step 3: Setup Python backend
echo ""
echo "[3/7] Setting up Python backend..."
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

# Step 4: Setup React frontend
echo ""
echo "[4/7] Setting up React frontend..."
cd "$INSTALL_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install --silent > /dev/null 2>&1
fi
echo "✓ Frontend dependencies installed"

# Step 5: Create systemd services
echo ""
echo "[5/7] Creating systemd services..."

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
ExecStart=/usr/bin/npx serve -s build -l $WEB_PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
WEBSERVICE

systemctl daemon-reload
echo "✓ Systemd services created"

# Step 6: Build frontend for production
echo ""
echo "[6/7] Building frontend for production..."
cd "$INSTALL_DIR/frontend"
npm run build --silent > /dev/null 2>&1
npm install -g serve --silent > /dev/null 2>&1
echo "✓ Frontend built"

# Step 7: Start services
echo ""
echo "[7/7] Starting services..."
systemctl enable vrhost-api > /dev/null 2>&1
systemctl enable vrhost-web > /dev/null 2>&1
systemctl start vrhost-api
systemctl start vrhost-web
echo "✓ Services started and enabled"

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "============================================"
echo "   ✅ VRHost Lab Installation Complete!"
echo "============================================"
echo ""
echo "🌐 Web Interface: http://$SERVER_IP:$WEB_PORT"
echo "📡 API Server:    http://$SERVER_IP:$API_PORT"
echo "📚 API Docs:      http://$SERVER_IP:$API_PORT/docs"
echo ""
echo "📊 Service Status:"
echo "   systemctl status vrhost-api"
echo "   systemctl status vrhost-web"
echo ""
echo "🔧 Service Commands:"
echo "   systemctl start|stop|restart vrhost-api"
echo "   systemctl start|stop|restart vrhost-web"
echo ""
echo "📝 Logs:"
echo "   journalctl -u vrhost-api -f"
echo "   journalctl -u vrhost-web -f"
echo ""
echo "🚀 Ready to create labs!"
echo ""
