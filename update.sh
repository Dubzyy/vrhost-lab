#!/bin/bash

# VRHost Lab Updater

set -e

INSTALL_DIR="/opt/vrhost-lab"

echo "============================================"
echo "   VRHost Lab - Update"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "[1/4] Pulling latest changes from Git..."
cd "$INSTALL_DIR"
git pull

echo ""
echo "[2/4] Updating Python dependencies..."
source venv/bin/activate
pip install --quiet --upgrade \
    fastapi \
    uvicorn[standard] \
    libvirt-python \
    pydantic \
    websockets \
    python-multipart

echo ""
echo "[3/4] Updating frontend dependencies and rebuilding..."
cd "$INSTALL_DIR/frontend"
npm install --silent > /dev/null 2>&1
npm run build --silent > /dev/null 2>&1

echo ""
echo "[4/4] Restarting services..."
systemctl restart vrhost-api
systemctl restart vrhost-web

echo ""
echo "✅ VRHost Lab updated successfully!"
echo ""
systemctl status vrhost-api --no-pager -l
echo ""
systemctl status vrhost-web --no-pager -l
echo ""
