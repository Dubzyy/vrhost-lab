#!/bin/bash

# VRHost Lab Uninstaller

set -e

echo "============================================"
echo "   VRHost Lab - Uninstallation"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

read -p "⚠️  This will remove VRHost Lab services. Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "Stopping services..."
systemctl stop vrhost-api 2>/dev/null || true
systemctl stop vrhost-web 2>/dev/null || true

echo "Disabling services..."
systemctl disable vrhost-api 2>/dev/null || true
systemctl disable vrhost-web 2>/dev/null || true

echo "Removing service files..."
rm -f /etc/systemd/system/vrhost-api.service
rm -f /etc/systemd/system/vrhost-web.service

systemctl daemon-reload

echo ""
echo "✅ VRHost Lab services removed"
echo ""
echo "Note: Installation directory /opt/vrhost-lab was NOT deleted."
echo "To completely remove: rm -rf /opt/vrhost-lab"
echo ""
