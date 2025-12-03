# VRHost Lab - Installation Guide

## Quick Install (Recommended)

**One-command installation on Ubuntu 22.04+:**
```bash
# Clone repository
git clone https://github.com/Dubzyy/vrhost-lab.git
cd vrhost-lab

# Run installer
sudo ./install.sh
```

The installer will:
- ✅ Install all dependencies (libvirt, Node.js, Python packages)
- ✅ Set up backend and frontend
- ✅ Create systemd services
- ✅ Build production frontend
- ✅ Start services automatically
- ✅ Enable services on boot

**Installation takes ~5 minutes**

## Post-Installation

Access VRHost Lab:
- **Web Interface:** `http://YOUR_SERVER_IP:3000`
- **API Server:** `http://YOUR_SERVER_IP:8000`
- **API Docs:** `http://YOUR_SERVER_IP:8000/docs`

## Managing Services
```bash
# Check status
systemctl status vrhost-api
systemctl status vrhost-web

# Start/Stop/Restart
systemctl start vrhost-api
systemctl stop vrhost-api
systemctl restart vrhost-api

# View logs
journalctl -u vrhost-api -f
journalctl -u vrhost-web -f
```

## Updating
```bash
cd /opt/vrhost-lab
sudo ./update.sh
```

## Uninstalling
```bash
cd /opt/vrhost-lab
sudo ./uninstall.sh

# To completely remove (including data):
sudo rm -rf /opt/vrhost-lab
```

## Manual Installation

See [README.md](README.md) for manual installation steps.

## Troubleshooting

### Services won't start
```bash
# Check logs
journalctl -u vrhost-api -n 50
journalctl -u vrhost-web -n 50

# Check libvirt
systemctl status libvirtd
```

### Port conflicts
Edit service files:
```bash
sudo nano /etc/systemd/system/vrhost-api.service
sudo nano /etc/systemd/system/vrhost-web.service
sudo systemctl daemon-reload
sudo systemctl restart vrhost-api vrhost-web
```

### Permission issues
```bash
# Ensure libvirt access
sudo usermod -aG libvirt root
sudo systemctl restart libvirtd
```

## Requirements

- Ubuntu 22.04+ or Debian 11+ (recommended)
- 4GB RAM minimum (8GB+ recommended)
- KVM/QEMU capable CPU
- 50GB disk space minimum
- Root access

## Support

- GitHub Issues: https://github.com/Dubzyy/vrhost-lab/issues
- Email: admin@vrhost.org
