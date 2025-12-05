# VRHost Lab 🚀

<div align="center">

**A Modern, Web-Based Multi-Vendor Network Lab Platform**

Built for certification studies, network automation, and hands-on learning

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com/Dubzyy/vrhost-lab)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61dafb)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Dubzyy/vrhost-lab?style=social)](https://github.com/Dubzyy/vrhost-lab)

[**🎯 Features**](#-features) • [**🚀 Quick Start**](#-quick-start) • [**📖 Documentation**](#-documentation) • [**🗺️ Roadmap**](#️-roadmap)

</div>

---

## 📖 Overview

VRHost Lab is a lightweight, web-based platform for managing multi-vendor virtual network labs. It provides an intuitive interface for creating, managing, and accessing Juniper and Cisco routers and switches through your browser - perfect for studying for certifications like JNCIS-SP, CCNA, or building complex network topologies for testing.

**Think EVE-NG/GNS3, but modern, lightweight, and built from the ground up for ease of use.**

### 🎯 Why VRHost Lab?

- ✅ **Multi-vendor support** - Juniper vSRX, Cisco CSR1000v, and Cisco IOSvL2 switches
- ✅ **One-command installation** - Up and running in under 5 minutes
- ✅ **Browser-based console** - No SSH client needed, access devices directly in your browser
- ✅ **Interactive topology view** - Visual network diagrams that update in real-time
- ✅ **Modern tech stack** - FastAPI backend + React frontend = fast and responsive
- ✅ **Open source** - Free to use, modify, and contribute

---

## ✨ Features

### 🖥️ **Web-Based Console Access**
Click "Console" and you're in - no SSH client required. Powered by ttyd for secure, token-based terminal sessions.

- Multiple concurrent console sessions
- Works through SSH tunnels and SOCKS proxies
- Session timeout and automatic cleanup
- Perfect for remote lab access
- Supports Juniper, Cisco routers, and switches

### 🌐 **Interactive Network Topology**
Beautiful, real-time topology visualization powered by Cytoscape.js.

- **Color-coded status** - Green (running), Blue (starting), Yellow (stopping), Gray (stopped)
- **Vendor badges** - Blue for Cisco devices, Green for Juniper devices
- **Device type identification** - Routers vs switches clearly labeled
- **Drag-and-drop positioning** - Arrange your topology exactly how you want
- **Multiple layouts** - Circle, Grid, or custom arrangements
- **Live updates** - Status changes reflected immediately
- **Click for details** - Select nodes to see device info

### 🏗️ **Multi-Lab Management**
Organize devices into isolated lab environments.

- Create separate labs for different projects or study topics
- Start/stop entire labs with one click
- Mix Juniper and Cisco devices in the same lab
- Track resource usage per lab
- Filter and search across labs

### 🔀 **Multi-Vendor Support**
Work with multiple router and switch vendors in the same platform.

- **Juniper vSRX** - Full support for virtual firewall/router
- **Cisco CSR1000v** - Cloud Services Router for modern labs
- **Cisco IOSvL2** - Layer 2/3 switch with 16 ports
- Visual vendor identification with color-coded badges
- Vendor-specific boot time warnings
- Unified interface for all platforms

### ⚡ **Quick Actions**
Manage devices efficiently with optimistic UI updates.

- **Start/Stop/Restart** - Control device lifecycle
- **Delete with confirmation** - Prevent accidental deletions
- **Bulk operations** - Manage multiple devices at once
- **Real-time status** - See changes immediately

### 📊 **Real-Time Monitoring**
Track system resources and device states.

- CPU and memory usage per device
- Running vs total devices
- Vendor distribution
- Lab statistics
- System health monitoring

### 🔐 **Remote Access Ready**
Built with remote access in mind.

- SSH tunnel support
- SOCKS proxy compatibility
- Tailscale integration
- Secure by default

---

## 🛠️ Technology Stack

<table>
<tr>
<td width="50%">

**Backend**
- 🐍 Python 3.11+
- ⚡ FastAPI (ASGI framework)
- 🖥️ libvirt for KVM/QEMU
- 💻 ttyd for web terminals
- 🦄 uvicorn server

</td>
<td width="50%">

**Frontend**
- ⚛️ React 18.3
- 🎨 Tailwind CSS
- 📊 Cytoscape.js
- 🔗 Axios HTTP client
- 📱 Responsive design

</td>
</tr>
<tr>
<td width="50%">

**Infrastructure**
- 🔧 KVM/QEMU virtualization
- 🔄 systemd services
- 🌉 Linux bridge networking
- 🐧 Ubuntu 22.04+

</td>
<td width="50%">

**Supported Platforms**
- ✅ **Juniper vSRX** (router)
- ✅ **Cisco CSR1000v** (router)
- ✅ **Cisco IOSvL2** (switch)
- 🔜 Juniper vQFX (planned)

</td>
</tr>
</table>

---

## 🌐 Supported Platforms

### ✅ Production Ready - Routers
- **Juniper vSRX** - Virtual firewall/router
  - Resources: 4GB RAM, 2 vCPU
  - Boot time: ~90 seconds
  - Features: Full JunOS, security policies, routing protocols

- **Cisco CSR1000v** - Cloud Services Router
  - Resources: 4GB RAM, 2 vCPU
  - Boot time: ~3-5 minutes
  - Features: Full IOS XE, MPLS, SD-WAN, VPN

### ✅ Production Ready - Switches
- **Cisco IOSvL2** - Layer 2/3 switch
  - Resources: 2GB RAM, 2 vCPU
  - Boot time: ~2-3 minutes
  - Features: 16 ports (Gi0/0-Gi3/3), VLANs, STP, trunking, L3 routing

### 🔜 Planned (Phase 3)
- **Juniper vQFX** - Virtual QFX switch
- **Arista vEOS** - Virtual Arista switch
- **Cisco Nexus 9000v** - Data center switch

---

## 📋 Requirements

### System Requirements

| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|------------|
| **CPU** | 4 cores | 8 cores | 16+ cores |
| **RAM** | 16GB | 32GB | 64GB+ |
| **Disk** | 100GB | 250GB | 500GB+ SSD |
| **Devices** | 2-3 | 5-10 | 15+ |

**Resource Notes:**
- Juniper vSRX: 4GB RAM, 2 vCPU per router (minimum)
- Cisco CSR1000v: 4GB RAM, 2 vCPU per router (minimum)
- Cisco IOSvL2: 2GB RAM, 2 vCPU per switch (minimum)
- Plan ~8GB RAM overhead for host OS and services

### Software Prerequisites

- **OS**: Ubuntu 22.04 LTS or newer (Ubuntu 24.04 also supported)
- **Access**: Root or sudo privileges
- **Virtualization**: Intel VT-x or AMD-V (KVM support required)
- **Network**: Internet connection for dependencies
- **Device Images**: You must provide your own router/switch images (see below)

### Deployment Options

- ✅ **Bare Metal** (recommended) - Best performance for production labs
- ✅ **Virtual Machine** - Requires nested virtualization enabled on host
- ✅ **Cloud VM** - GCP (native nested virt), Azure (certain VM types)
- ⚠️ **VirtualBox** - Limited nested virtualization, not recommended

---

## 🚀 Quick Start

### Installation (5 minutes)
```bash
# 1. Clone repository
git clone https://github.com/Dubzyy/vrhost-lab.git
cd vrhost-lab

# 2. Run installer (installs all dependencies)
sudo bash install.sh

# 3. Installation complete! Services start automatically.
```

### What the Installer Does

- ✅ Installs Node.js 20.x, Python 3.11+, KVM, QEMU, libvirt, ttyd
- ✅ Creates Python virtual environment with FastAPI
- ✅ Builds React frontend for production
- ✅ Installs automation scripts (mkjuniper, mkcsr1000v, mkviosl2)
- ✅ Configures systemd services (vrhost-api, vrhost-web)
- ✅ Verifies KVM virtualization support
- ✅ Starts the platform automatically on port 3000

### Post-Installation: Add Device Images

**VRHost Lab does not include device images due to licensing restrictions. You must provide your own.**

#### Option 1: Juniper vSRX

1. **Download image:**
   - Visit: https://support.juniper.net/support/downloads/
   - Navigate to: vSRX → Juniper vSRX Virtual Firewall
   - Download latest `.qcow2` image (requires free Juniper account)
   - Recommended: vSRX 3.x (23.2R2 or newer)

2. **Install image:**
```bash
   # Create directory
   sudo mkdir -p /var/lib/libvirt/images/juniper

   # Move downloaded image
   sudo mv ~/Downloads/junos-vsrx3-*.qcow2 /var/lib/libvirt/images/juniper/

   # Set permissions
   sudo chmod 644 /var/lib/libvirt/images/juniper/*.qcow2
```

3. **Update script:**
```bash
   sudo nano /usr/local/bin/mkjuniper
   # Update line 13 with your image filename
```

#### Option 2: Cisco CSR1000v

1. **Download image:**
   - Visit: https://software.cisco.com/download/home
   - Search for: "CSR1000v"
   - Download: `csr1000vng-universalk9.17.03.04a-serial.tgz` or newer
   - Requires Cisco.com account (free registration)

2. **Install image:**
```bash
   # Extract archive
   cd ~/Downloads
   tar -xzf csr1000vng-universalk9.*.tgz

   # Create directory
   sudo mkdir -p /var/lib/libvirt/images/cisco

   # Move qcow2 file
   sudo mv */virtioa.qcow2 /var/lib/libvirt/images/cisco/csr1000v-17.03.04a.qcow2

   # Set permissions
   sudo chmod 644 /var/lib/libvirt/images/cisco/*.qcow2
```

3. **Update script:**
```bash
   sudo nano /usr/local/bin/mkcsr1000v
   # Update line 13 with your image filename
```

#### Option 3: Cisco IOSvL2 (Switch)

1. **Download image:**
   - Visit: https://software.cisco.com/download/home
   - Search for: "IOSvL2" or "VIRL IOSv L2"
   - Download: `viosl2-adventerprisek9-m.SSA.high_iron_*.tgz`
   - Requires Cisco.com account (free registration)

2. **Install image:**
```bash
   # Extract archive
   cd ~/Downloads
   tar -xzf viosl2-adventerprisek9-m.*.tgz

   # Create directory (if not exists)
   sudo mkdir -p /var/lib/libvirt/images/cisco

   # Move qcow2 file
   sudo mv viosl2-*/virtioa.qcow2 /var/lib/libvirt/images/cisco/viosl2-20180619.qcow2

   # Set permissions
   sudo chmod 644 /var/lib/libvirt/images/cisco/*.qcow2
```

3. **Update script:**
```bash
   sudo nano /usr/local/bin/mkviosl2
   # Update line 13 with your image filename
```

### Access the Platform

**Local access:**
```
http://localhost:3000
```

**Remote access:**
```
http://YOUR_SERVER_IP:3000
```

**API documentation:**
```
http://YOUR_SERVER_IP:8000/docs
```

### Create Your First Devices

**Option A: Juniper vSRX Router**
```bash
sudo mkjuniper r1
# Wait ~90 seconds for boot
# Access via web interface - click "Console" button
```

**Option B: Cisco CSR1000v Router**
```bash
sudo mkcsr1000v csr-r1
# Wait ~3-5 minutes for first boot
# Access via web interface - click "Console" button
```

**Option C: Cisco IOSvL2 Switch**
```bash
sudo mkviosl2 sw1
# Wait ~2-3 minutes for boot
# Access via web interface - click "Console" button
# 16 ports available: Gi0/0 through Gi3/3
```

**Via Web Interface:**
1. Click "+ New Device"
2. Enter name (e.g., "r1", "csr-r1", or "sw1")
3. Enter IP address (e.g., "10.10.50.11")
4. Select device type (Juniper Router, Cisco Router, or Cisco Switch)
5. Click "Create Device"
6. Wait for boot, then click "Console" to access CLI

---

## 🌐 Remote Access

### Method 1: SSH Tunnel (Simple)
```bash
# Forward both web and API ports
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 user@your-server
```

Then access: `http://localhost:3000`

**Limitations:** Console access won't work (ttyd sessions blocked)

### Method 2: SSH + SOCKS Proxy (Full Access)
```bash
# Create SOCKS proxy + port forwarding
ssh -D 8080 -L 3000:localhost:3000 -L 8000:localhost:8000 user@your-server
```

**Configure browser (Firefox recommended):**
1. Settings → Network Settings → Settings
2. Manual proxy configuration:
   - SOCKS Host: `localhost`, Port: `8080`
   - Select "SOCKS v5"
   - ✅ Enable "Proxy DNS when using SOCKS v5"

Access: `http://localhost:3000` (full console access works!)

### Method 3: Tailscale (Recommended for Remote)
```bash
# Install on server
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Get Tailscale IP
tailscale ip -4

# Install Tailscale on your computer
# Sign in with same account
# Access: http://100.x.x.x:3000
```

**Benefits:**
- ✅ Encrypted WireGuard tunnel
- ✅ Works from anywhere
- ✅ No port forwarding needed
- ✅ Full console access
- ✅ Cross-platform (Windows, Mac, Linux, mobile)

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      Web Browser (Port 3000)                     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Dashboard   │  │   Topology   │  │   Console (ttyd)     │  │
│  │   (React)    │  │ (Cytoscape)  │  │   Dynamic ports      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────────┘  │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          │                  │                  │
          │         HTTP/REST API + WebSocket   │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                         │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  RouterService  │  LabService   │  ConsoleService (ttyd)  │  │
│  │  StatsService   │  TopologyService                        │  │
│  └──────────┬──────────────┬──────────────┬──────────────────┘  │
└─────────────┼───────────────┼──────────────┼─────────────────────┘
              │               │              │
              ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    libvirt / KVM Layer                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Virtual Network (br0 bridge - 10.10.50.0/24)              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ Juniper  │  │ Juniper  │  │  Cisco   │  │    Cisco     │    │
│  │  vSRX-1  │  │  vSRX-2  │  │ CSR1000v │  │   IOSvL2-1   │    │
│  │ (Router) │  │ (Router) │  │ (Router) │  │   (Switch)   │    │
│  │ 4GB/2C   │  │ 4GB/2C   │  │ 4GB/2C   │  │   2GB/2C     │    │
│  │ ~90sec   │  │ ~90sec   │  │ ~3-5min  │  │   ~2-3min    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure
```
vrhost-lab/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main application entry
│   ├── models/                # Pydantic data models
│   │   ├── router.py          # Router/Switch model with multi-vendor support
│   │   ├── lab.py             # Lab model
│   │   └── topology.py        # Topology model
│   └── services/              # Business logic
│       ├── router_service.py  # Multi-vendor device management
│       ├── lab_service.py     # Lab management
│       ├── stats_service.py   # System statistics
│       └── console_service.py # Web console (ttyd integration)
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.js             # Main component with vendor support
│   │   ├── Topology.js        # Cytoscape topology with vendor badges
│   │   └── services/
│   │       └── api.js         # API client
│   ├── public/
│   ├── tailwind.config.js     # Dark theme configuration
│   └── package.json
│
├── scripts/                    # Automation scripts
│   ├── mkjuniper              # Create Juniper vSRX router
│   ├── mkcsr1000v             # Create Cisco CSR1000v router
│   ├── mkviosl2               # Create Cisco IOSvL2 switch
│   ├── mkvm                   # Generic VM creation utility
│   └── README.md              # Scripts documentation
│
├── docs/                       # Documentation
│   └── ROUTER_SETUP.md        # Router configuration guide
│
├── install.sh                 # One-command installer
├── README.md                  # This file
└── LICENSE                    # MIT License
```

---

## 🗺️ Roadmap

### ✅ Phase 1: Core Platform (Complete)
- ✅ FastAPI backend with REST API
- ✅ React frontend with Tailwind CSS dark theme
- ✅ Web console access via ttyd
- ✅ Interactive topology view with Cytoscape.js
- ✅ Multi-lab management
- ✅ One-command installer
- ✅ systemd service integration
- ✅ Real-time system monitoring

### ✅ Phase 2: Multi-Vendor Support (Complete)
- ✅ Juniper vSRX full support (production)
- ✅ Cisco CSR1000v full support (production)
- ✅ Cisco IOSvL2 switch support (production)
- ✅ Backend multi-vendor device detection
- ✅ Frontend vendor badges (blue=Cisco, green=Juniper)
- ✅ Automated provisioning scripts for all platforms
- ✅ Vendor-specific boot time handling
- ✅ Unified console access for routers and switches

### 🔮 Phase 3: Additional Platforms (In Progress)
- 🔄 Juniper vQFX switch support (researching)
- 🔜 Arista vEOS router/switch
- 🔜 VyOS router support
- 🔜 Cisco Nexus 9000v (data center)

### 🚀 Phase 4: Advanced Features (Planned)
- 🔜 Device snapshots and cloning
- 🔜 Configuration backup/restore automation
- 🔜 Lab templates (save/load full topologies)
- 🔜 Network diagram export (PNG/SVG)
- 🔜 Automated lab provisioning from YAML
- 🔜 Configuration versioning with Git integration
- 🔜 Bulk device operations

### 🌟 Phase 5: Platform Enhancement (Future)
- 🔜 User authentication (JWT-based)
- 🔜 Multi-user support with isolation
- 🔜 Role-based access control (RBAC)
- 🔜 Centralized logging (Graylog)
- 🔜 Metrics dashboard (Prometheus/Grafana)
- 🔜 API rate limiting
- 🔜 WebSocket for real-time updates
- 🔜 Email notifications for lab events

---

## 🎓 Perfect For

- 📚 **Certification Studies** - JNCIS-SP, JNCIA, CCNA, CCNP, CCIE lab practice
- 🔬 **Network Testing** - Protocol testing, feature validation, interoperability
- 🏫 **Training Labs** - Teaching network concepts, university courses
- 🔧 **Development** - Network automation development with Ansible/Python
- 📊 **Research** - Network behavior analysis, performance testing
- 💼 **Professional** - Pre-production testing, change validation, switching studies

---

## 🐛 Troubleshooting

### Services Not Starting
```bash
# Check service status
sudo systemctl status vrhost-api
sudo systemctl status vrhost-web

# View logs
sudo journalctl -u vrhost-api -f
sudo journalctl -u vrhost-web -f

# Common fixes
sudo systemctl restart vrhost-api vrhost-web
sudo systemctl daemon-reload
```

### Device Won't Boot
```bash
# Check VM status
virsh list --all
virsh dominfo device-name

# Check KVM support
sudo kvm-ok

# View VM console directly
virsh console device-name
# Press Ctrl+] to exit

# Check libvirt logs
sudo journalctl -t libvirtd -f
```

### Console Session Stuck
```bash
# Check ttyd processes
ps aux | grep ttyd

# Kill stuck sessions
sudo pkill -9 ttyd

# Restart API to recreate console service
sudo systemctl restart vrhost-api
```

### Frontend Not Loading
```bash
# Check web service
sudo systemctl status vrhost-web

# Rebuild frontend
cd /opt/vrhost-lab/frontend
npm install
npm run build
sudo systemctl restart vrhost-web

# Clear browser cache (Ctrl+Shift+R)
```

### Image Boot Issues

**Juniper vSRX:**
- Verify image path in `/usr/local/bin/mkjuniper`
- Ensure image is qcow2 format
- Check permissions: `sudo chmod 644 /var/lib/libvirt/images/juniper/*.qcow2`
- Boot time: ~90 seconds (be patient!)

**Cisco CSR1000v:**
- Verify image path in `/usr/local/bin/mkcsr1000v`
- First boot takes 3-5 minutes (hardware initialization)
- Subsequent boots: ~2 minutes
- Use VNC if available: `virsh vncdisplay device-name`

**Cisco IOSvL2:**
- Verify image path in `/usr/local/bin/mkviosl2`
- Boot time: ~2-3 minutes
- Shows 16 ports: Gi0/0 through Gi3/3
- Some error messages during boot are normal (NVRAM warnings)

**Note on Cisco IOSv:** Traditional IOSv router images have compatibility issues with modern KVM. Use CSR1000v for routing instead. IOSvL2 is specifically designed for switching and works reliably.

### Network Connectivity Issues
```bash
# Check bridge
ip link show br0
brctl show

# Restart libvirt network
sudo virsh net-destroy default
sudo virsh net-start default

# Check device interfaces
virsh domiflist device-name
```

**For more help**, open an issue on [GitHub Issues](https://github.com/Dubzyy/vrhost-lab/issues).

---

## 🤝 Contributing

Contributions are welcome! Whether it's:

- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🔧 Code contributions
- 🧪 Testing on different platforms

**How to contribute:**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Backend development
cd /opt/vrhost-lab/backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd /opt/vrhost-lab/frontend
npm install
npm start  # Runs on port 3000 with hot reload
```

### Testing
```bash
# Test device creation
sudo mkjuniper test-r1
sudo mkcsr1000v test-csr1
sudo mkviosl2 test-sw1

# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/routers

# Check logs
sudo journalctl -u vrhost-api -f
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**You are free to:**
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute
- ✅ Use privately

**You must:**
- 📋 Include copyright notice
- 📋 Include license text

---

## 🙏 Acknowledgments

- **Inspired by**: EVE-NG and GNS3 - the pioneers of network lab virtualization
- **Built for**: Network engineers studying for Juniper and Cisco certifications
- **Powered by**:
  - [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
  - [React](https://reactjs.org/) - UI library for building user interfaces
  - [Cytoscape.js](https://js.cytoscape.org/) - Graph visualization and analysis
  - [ttyd](https://github.com/tsl0922/ttyd) - Share your terminal over the web
  - [libvirt](https://libvirt.org/) - Virtualization API and management
  - [KVM](https://www.linux-kvm.org/) - Kernel-based Virtual Machine
  - [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

---

## 📧 Contact & Support

**Author**: Hunter Wilson
*Network Engineer | Full-Stack Developer*

- 🐙 GitHub: [@Dubzyy](https://github.com/Dubzyy)
- 💼 LinkedIn: [Hunter Wilson](https://linkedin.com/in/hunter-wilsonit)
- 🌐 Portfolio: [https://portfolio.vrhost.org](https://portfolio.vrhost.org)
- 📧 Email: admin@vrhost.org

**Project Links**:

- 🔗 Repository: [https://github.com/Dubzyy/vrhost-lab](https://github.com/Dubzyy/vrhost-lab)
- 🐛 Issues: [https://github.com/Dubzyy/vrhost-lab/issues](https://github.com/Dubzyy/vrhost-lab/issues)
- 💬 Discussions: [https://github.com/Dubzyy/vrhost-lab/discussions](https://github.com/Dubzyy/vrhost-lab/discussions)
- ⭐ Give us a star: [Star on GitHub](https://github.com/Dubzyy/vrhost-lab)

---

<div align="center">

**⭐ If you find VRHost Lab useful, please star this repository! ⭐**

**Built with ❤️ for the network engineering community**

[![GitHub stars](https://img.shields.io/github/stars/Dubzyy/vrhost-lab?style=social)](https://github.com/Dubzyy/vrhost-lab)
[![GitHub forks](https://img.shields.io/github/forks/Dubzyy/vrhost-lab?style=social)](https://github.com/Dubzyy/vrhost-lab/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/Dubzyy/vrhost-lab?style=social)](https://github.com/Dubzyy/vrhost-lab)

[🚀 Get Started](#-quick-start) • [📖 Documentation](#-documentation) • [🐛 Report Bug](https://github.com/Dubzyy/vrhost-lab/issues) • [💡 Request Feature](https://github.com/Dubzyy/vrhost-lab/issues)

---

**VRHost Lab** - Your gateway to mastering network engineering

*Making network labs accessible, modern, and enjoyable*

</div>
