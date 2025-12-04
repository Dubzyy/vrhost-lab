# VRHost Lab - Installation Guide

Complete step-by-step installation guide for VRHost Lab on Ubuntu 22.04+.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Pre-Installation Checks](#pre-installation-checks)
- [Quick Installation](#quick-installation)
- [Post-Installation Setup](#post-installation-setup)
- [Creating Your First Router](#creating-your-first-router)
- [Remote Access Configuration](#remote-access-configuration)
- [Service Management](#service-management)
- [Updating VRHost Lab](#updating-vrhost-lab)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## 🎯 Prerequisites

### Hardware Requirements

| Requirement | Minimum | Recommended | Production |
|-------------|---------|-------------|------------|
| **CPU Cores** | 4 | 8 | 16+ |
| **RAM** | 16GB | 32GB | 64GB+ |
| **Disk Space** | 100GB | 250GB | 500GB+ SSD |
| **Network** | 1 Gbps | 1 Gbps | 10 Gbps |

### Software Requirements

- **Operating System**: Ubuntu 22.04 LTS or newer (Ubuntu 24.04 also supported)
- **Access Level**: Root or sudo privileges
- **Virtualization**: CPU with Intel VT-x or AMD-V support
- **Network**: Active internet connection for package downloads

### Supported Deployment Platforms

- ✅ **Bare Metal Servers** (Recommended) - Best performance
- ✅ **Virtual Machines** (Requires nested virtualization enabled)
- ✅ **Cloud VMs** (GCP, Azure with nested virt support)

---

## 🔍 Pre-Installation Checks

### Step 1: Verify CPU Virtualization Support
```bash
# Check for virtualization extensions
egrep -c '(vmx|svm)' /proc/cpuinfo
```

**Expected Output**: A number greater than 0
- `vmx` = Intel VT-x
- `svm` = AMD-V

### Step 2: Verify KVM Support
```bash
# Install CPU checker
sudo apt update
sudo apt install -y cpu-checker

# Check KVM availability
sudo kvm-ok
```

**Expected Output**:
```
INFO: /dev/kvm exists
KVM acceleration can be used
```

If you see `KVM acceleration can NOT be used`, you need to:
1. Enable virtualization in BIOS/UEFI
2. If on a VM, enable nested virtualization on the host

### Step 3: Check Available Resources
```bash
# Check RAM
free -h

# Check disk space
df -h /

# Check CPU details
lscpu | grep -E 'CPU\(s\)|Model name|Virtualization'
```

**Minimum Requirements**:
- RAM: At least 8GB free
- Disk: At least 50GB free on `/`
- CPU: Virtualization enabled

---

## 🚀 Quick Installation

### One-Command Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/Dubzyy/vrhost-lab.git
cd vrhost-lab

# Run the installer
sudo bash install.sh
```

### What the Installer Does

The installation script automatically:

1. **Updates System Packages**
   - Runs `apt update` and `apt upgrade`
   - Ensures package lists are current

2. **Installs KVM/QEMU and libvirt**
   - `qemu-kvm` - QEMU virtualization
   - `libvirt-daemon-system` - libvirt daemon
   - `libvirt-clients` - virsh CLI tools
   - `bridge-utils` - Network bridging
   - `virt-manager` - Optional GUI (if X11 available)

3. **Installs Node.js 20.x**
   - Adds NodeSource repository
   - Installs Node.js and npm
   - Used for React frontend

4. **Installs Python 3.11+**
   - Python 3 and pip
   - Python virtual environment tools
   - Required for FastAPI backend

5. **Installs ttyd**
   - Web-based terminal emulator
   - Enables browser console access

6. **Sets Up Project Structure**
   - Copies files to `/opt/vrhost-lab`
   - Creates Python virtual environment
   - Installs Python dependencies (FastAPI, uvicorn, libvirt-python)

7. **Builds Frontend**
   - Runs `npm install` in frontend directory
   - Builds production React bundle
   - Optimizes assets for deployment

8. **Creates systemd Services**
   - `vrhost-api.service` - Backend API (port 8000)
   - `vrhost-web.service` - Frontend web server (port 3000)
   - Enables automatic startup on boot

9. **Starts Services**
   - Starts both services
   - Verifies they're running correctly

### Installation Output

You'll see progress messages like:
```
[✓] Installing system dependencies...
[✓] Installing Node.js 20.x...
[✓] Installing Python dependencies...
[✓] Building React frontend...
[✓] Creating systemd services...
[✓] Starting services...

Installation complete!

Access VRHost Lab at:
  Web Interface: http://YOUR_SERVER_IP:3000
  API Server:    http://YOUR_SERVER_IP:8000
  API Docs:      http://YOUR_SERVER_IP:8000/docs
```

**Installation Time**: 5-10 minutes (depends on internet speed)

---

## ⚙️ Post-Installation Setup

### Step 1: Verify Services Are Running
```bash
# Check API service
sudo systemctl status vrhost-api

# Check web service
sudo systemctl status vrhost-web

# Both should show: Active: active (running)
```

### Step 2: Test Web Interface

**Local Access**:
```bash
# Test API
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:3000
```

**Remote Access** (from your laptop):
```bash
# Replace YOUR_SERVER_IP with actual IP
curl http://YOUR_SERVER_IP:8000/api/health
```

**Browser Access**:
- Navigate to: `http://YOUR_SERVER_IP:3000`
- You should see the VRHost Lab dashboard

### Step 3: Download Router Images

VRHost Lab requires Juniper vSRX images (not included due to licensing).

**Option A: Official Juniper Download**

1. Visit: https://support.juniper.net/support/downloads/
2. Navigate to: vSRX → Juniper vSRX Virtual Firewall
3. Download: `junos-vsrx3-x86-64-*.qcow2` (latest version)
4. Requires free Juniper account

**Option B: EVE-NG Community**

Check EVE-NG community forums for compatible images.

**Place the image:**
```bash
# Create directory
sudo mkdir -p /var/lib/libvirt/images/juniper

# Move your downloaded image (adjust filename)
sudo mv ~/Downloads/junos-vsrx3-*.qcow2 /var/lib/libvirt/images/juniper/

# Set permissions
sudo chmod 644 /var/lib/libvirt/images/juniper/*.qcow2

# Verify
ls -lh /var/lib/libvirt/images/juniper/
```

### Step 4: Configure mkjuniper Script
```bash
# Edit the script
sudo nano /usr/local/bin/mkjuniper
```

**Find this line (around line 13):**
```bash
IMAGE_PATH="/var/lib/libvirt/images/juniper/vsrx3-23.2R2.21.qcow2"
```

**Update with your actual image filename:**
```bash
IMAGE_PATH="/var/lib/libvirt/images/juniper/junos-vsrx3-YOUR-VERSION.qcow2"
```

**Save**: Ctrl+O, Enter, Ctrl+X

---

## 🎬 Creating Your First Router

### Method 1: Command Line (Quick)
```bash
# Create a router named "r1"
sudo mkjuniper r1

# Wait 2-3 minutes for boot, then check status
virsh list

# Connect to console
virsh console r1
# (Press Enter a few times to see prompt)
# Login: root (no password)
# Exit console: Ctrl+]
```

### Method 2: Web Interface (Recommended)

1. **Open Web Interface**
   - Navigate to: `http://YOUR_SERVER_IP:3000`

2. **Create a Lab** (Optional but recommended)
   - Click "+ New Lab" button
   - Name: `my-first-lab`
   - Description: "Learning JNCIS-SP"
   - Click "Create"

3. **Create a Router**
   - Click "+ New Router" button
   - Name: `r1`
   - Lab: Select "my-first-lab"
   - Click "Create"
   - Wait 2-3 minutes for router to boot

4. **Access Console**
   - Wait for router status to turn green (running)
   - Click "Console" button
   - New window opens with terminal
   - Login: `root` (no password initially)

5. **Basic Configuration**
```
   root@r1> configure
   root@r1# set system host-name r1
   root@r1# set system root-authentication plain-text-password
   New password: <your-password>
   Retype new password: <your-password>
   root@r1# commit
   root@r1# exit
```

### Viewing Topology

1. Click "🌐 Topology View" tab
2. See visual representation of your routers
3. Drag nodes to rearrange
4. Click nodes for details
5. Use layout buttons to organize

---

## 🌐 Remote Access Configuration

### Method 1: SSH Tunnel (Simple)

**For Web Interface Only**:
```bash
# From your laptop
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 user@YOUR_SERVER_IP

# Then access in browser:
http://localhost:3000
```

### Method 2: SSH + SOCKS Proxy (For Console Access)

**For Full Functionality (including web console)**:
```bash
# From your laptop
ssh -D 8080 -L 3000:localhost:3000 -L 8000:localhost:8000 user@YOUR_SERVER_IP
```

**Configure Firefox SOCKS Proxy**:
1. Open Firefox Settings
2. Network Settings → Settings
3. Manual proxy configuration:
   - SOCKS Host: `localhost`
   - Port: `8080`
   - SOCKS v5: Enabled
   - ✅ Proxy DNS when using SOCKS v5
4. Access: `http://localhost:3000`

### Method 3: Tailscale (Recommended for Remote)

**On Server**:
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Connect to Tailscale
sudo tailscale up

# Note the Tailscale IP (100.x.x.x)
tailscale ip -4
```

**On Your Computer**:
1. Install Tailscale: https://tailscale.com/download
2. Sign in with same account
3. Access: `http://100.x.x.x:3000` (use Tailscale IP)

---

## 🔧 Service Management

### Checking Status
```bash
# API service
sudo systemctl status vrhost-api

# Web service  
sudo systemctl status vrhost-web

# Both services
sudo systemctl status vrhost-*
```

### Starting/Stopping Services
```bash
# Start
sudo systemctl start vrhost-api
sudo systemctl start vrhost-web

# Stop
sudo systemctl stop vrhost-api
sudo systemctl stop vrhost-web

# Restart
sudo systemctl restart vrhost-api vrhost-web
```

### Viewing Logs
```bash
# Live logs (follow mode)
sudo journalctl -u vrhost-api -f
sudo journalctl -u vrhost-web -f

# Last 50 lines
sudo journalctl -u vrhost-api -n 50
sudo journalctl -u vrhost-web -n 50

# Today's logs
sudo journalctl -u vrhost-api --since today
```

### Enabling/Disabling Autostart
```bash
# Enable (start on boot)
sudo systemctl enable vrhost-api
sudo systemctl enable vrhost-web

# Disable
sudo systemctl disable vrhost-api
sudo systemctl disable vrhost-web

# Check if enabled
systemctl is-enabled vrhost-api
```

---

## 🔄 Updating VRHost Lab

### Update from GitHub
```bash
# Navigate to installation directory
cd /opt/vrhost-lab

# Pull latest changes
git pull origin main

# Rebuild frontend
cd frontend
npm install
npm run build

# Restart services
sudo systemctl restart vrhost-api vrhost-web
```

### Check for Updates
```bash
# Check current version/commit
cd /opt/vrhost-lab
git log -1 --oneline

# Check for updates
git fetch origin
git log HEAD..origin/main --oneline
```

---

## 🐛 Troubleshooting

### Services Won't Start

**Problem**: systemctl status shows failed/inactive

**Solution**:
```bash
# Check detailed error logs
sudo journalctl -u vrhost-api -xe
sudo journalctl -u vrhost-web -xe

# Common fixes:
# 1. Port already in use
sudo netstat -tlnp | grep -E '3000|8000'
sudo fuser -k 3000/tcp  # Kill process on port 3000
sudo fuser -k 8000/tcp  # Kill process on port 8000

# 2. Permission issues
sudo chown -R root:root /opt/vrhost-lab
sudo chmod +x /opt/vrhost-lab/backend/venv/bin/uvicorn

# 3. Missing dependencies
cd /opt/vrhost-lab/backend
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo systemctl restart vrhost-api vrhost-web
```

### Router Won't Boot

**Problem**: Router created but won't start

**Solution**:
```bash
# Check router status
virsh list --all
virsh dominfo ROUTER_NAME

# Check for errors
virsh start ROUTER_NAME
# Read error message

# Common issues:
# 1. Image path incorrect
sudo nano /usr/local/bin/mkjuniper
# Verify IMAGE_PATH points to correct file

# 2. Insufficient RAM
virsh edit ROUTER_NAME
# Increase <memory> and <currentMemory> to 4194304 (4GB)

# 3. KVM not working
sudo kvm-ok
sudo systemctl restart libvirtd

# Delete and recreate router
virsh destroy ROUTER_NAME
virsh undefine ROUTER_NAME
rm /var/lib/libvirt/images/ROUTER_NAME.qcow2
sudo mkjuniper ROUTER_NAME
```

### Console Won't Open

**Problem**: Clicking "Console" button shows error

**Solution**:
```bash
# 1. Check if ttyd is installed
which ttyd
ttyd --version

# Install if missing
sudo apt install -y ttyd

# 2. Check console sessions
ps aux | grep ttyd

# 3. Check API logs for console errors
sudo journalctl -u vrhost-api | grep console

# 4. Test manual console access
virsh console ROUTER_NAME
# If this works, it's a ttyd/API issue
# If this doesn't work, it's a libvirt issue

# 5. Restart API service
sudo systemctl restart vrhost-api
```

### Frontend Not Loading

**Problem**: Web interface shows blank page or errors

**Solution**:
```bash
# 1. Check web service
sudo systemctl status vrhost-web
sudo journalctl -u vrhost-web -n 50

# 2. Check if frontend is built
ls -la /opt/vrhost-lab/frontend/build/

# 3. Rebuild frontend
cd /opt/vrhost-lab/frontend
rm -rf build node_modules
npm install
npm run build

# 4. Fix permissions
sudo chown -R root:root /opt/vrhost-lab/frontend/build

# 5. Restart service
sudo systemctl restart vrhost-web

# 6. Check for build errors
cd /opt/vrhost-lab/frontend
npm run build
# Read output for errors
```

### Network Issues

**Problem**: Routers have no network connectivity

**Solution**:
```bash
# Check bridge interface
ip link show br0
brctl show br0

# Recreate bridge if needed
sudo virsh net-destroy default
sudo virsh net-start default

# Check router network interfaces
virsh domiflist ROUTER_NAME

# Inside router, check interfaces
virsh console ROUTER_NAME
> show interfaces terse
```

---

## 🗑️ Uninstallation

### Remove Services Only
```bash
# Stop services
sudo systemctl stop vrhost-api vrhost-web

# Disable services
sudo systemctl disable vrhost-api vrhost-web

# Remove service files
sudo rm /etc/systemd/system/vrhost-api.service
sudo rm /etc/systemd/system/vrhost-web.service

# Reload systemd
sudo systemctl daemon-reload
```

### Complete Removal
```bash
# Stop and remove services (as above)
sudo systemctl stop vrhost-api vrhost-web
sudo systemctl disable vrhost-api vrhost-web
sudo rm /etc/systemd/system/vrhost-*.service
sudo systemctl daemon-reload

# Remove installation directory
sudo rm -rf /opt/vrhost-lab

# Remove scripts
sudo rm /usr/local/bin/mkjuniper
sudo rm /usr/local/bin/mkvm

# Remove router VMs (CAUTION: This deletes all routers!)
for vm in $(virsh list --all --name | grep -E '^r[0-9]+$|^Test-'); do
    virsh destroy "$vm" 2>/dev/null
    virsh undefine "$vm" 2>/dev/null
done

# Remove router disk images (CAUTION!)
sudo rm -rf /var/lib/libvirt/images/r*.qcow2
sudo rm -rf /var/lib/libvirt/images/Test-*.qcow2

# Optionally remove dependencies (if not used by other software)
# sudo apt remove --purge qemu-kvm libvirt-daemon-system nodejs ttyd
```

---

## 📚 Next Steps

After installation:

1. **Read Documentation**
   - [Router Setup Guide](ROUTER_SETUP.md)
   - [API Documentation](http://localhost:8000/docs)

2. **Create Multiple Routers**
   - Build a full lab topology
   - Practice BGP, OSPF, MPLS configurations

3. **Study for Certifications**
   - JNCIS-SP
   - JNCIA
   - Network engineering practice

4. **Contribute**
   - Report bugs: https://github.com/Dubzyy/vrhost-lab/issues
   - Submit improvements
   - Share your experience

---

## 📧 Support

- **GitHub Issues**: https://github.com/Dubzyy/vrhost-lab/issues
- **Discussions**: https://github.com/Dubzyy/vrhost-lab/discussions
- **Author**: Hunter Wilson - [@Dubzyy](https://github.com/Dubzyy)

---

**Installation complete! Start building your network labs!** 🎉
