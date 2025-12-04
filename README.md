# VRHost Lab 🚀

<div align="center">

**A Modern, Web-Based Network Lab Platform for Network Engineers**

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

VRHost Lab is a lightweight, web-based platform for managing virtual network labs. It provides an intuitive interface for creating, managing, and accessing network routers through your browser - perfect for studying for certifications like JNCIS-SP, CCNA, or building complex network topologies for testing.

**Think EVE-NG/GNS3, but modern, lightweight, and built from the ground up for ease of use.**

### 🎯 Why VRHost Lab?

- ✅ **One-command installation** - Up and running in under 5 minutes
- ✅ **Browser-based console** - No SSH client needed, access routers directly in your browser
- ✅ **Interactive topology view** - Visual network diagrams that update in real-time
- ✅ **Modern tech stack** - FastAPI backend + React frontend = fast and responsive
- ✅ **Multi-vendor ready** - Juniper support now, Cisco IOSv coming soon
- ✅ **Open source** - Free to use, modify, and contribute

---

## ✨ Features

### 🖥️ **Web-Based Console Access**
Click "Console" and you're in - no SSH client required. Powered by ttyd for secure, token-based terminal sessions.

- Multiple concurrent console sessions
- Works through SSH tunnels and SOCKS proxies
- Session timeout and automatic cleanup
- Perfect for remote lab access

### 🌐 **Interactive Network Topology**
Beautiful, real-time topology visualization powered by Cytoscape.js.

- **Color-coded status** - Green (running), Blue (starting), Yellow (stopping), Gray (stopped)
- **Drag-and-drop positioning** - Arrange your topology exactly how you want
- **Multiple layouts** - Circle, Grid, or custom arrangements
- **Live updates** - Status changes reflected immediately
- **Click for details** - Select nodes to see router info

### 🏗️ **Multi-Lab Management**
Organize routers into isolated lab environments.

- Create separate labs for different projects or study topics
- Start/stop entire labs with one click
- Track resource usage per lab
- Filter and search across labs

### ⚡ **Quick Actions**
Manage routers efficiently with optimistic UI updates.

- **Start/Stop/Restart** - Control router lifecycle
- **Delete with confirmation** - Prevent accidental deletions
- **Bulk operations** - Manage multiple routers at once
- **Real-time status** - See changes immediately

### 📊 **Real-Time Monitoring**
Track system resources and router states.

- CPU and memory usage per router
- Running vs total routers
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
- ✅ Juniper vSRX (production-ready)
- 🔜 Cisco IOSv (coming soon)
- 🔜 Cisco IOSvL2 (coming soon)
- 🔜 More vendors planned

</td>
</tr>
</table>

---

## 📋 Requirements

### System Requirements

| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|------------|
| **CPU** | 4 cores | 8 cores | 16+ cores |
| **RAM** | 16GB | 32GB | 64GB+ |
| **Disk** | 100GB | 250GB | 500GB+ SSD |
| **Routers** | 2-3 | 5-10 | 15+ |

### Software Prerequisites

- **OS**: Ubuntu 22.04 LTS or newer
- **Access**: Root or sudo privileges
- **Virtualization**: Intel VT-x or AMD-V (KVM support)
- **Network**: Internet connection for dependencies
- **Router Images**: Juniper vSRX (download separately)

### Deployment Options

- ✅ **Bare Metal** (recommended) - Best performance
- ✅ **Virtual Machine** - Requires nested virtualization
- ✅ **Cloud VM** - GCP, Azure with nested virt support

---

## 🚀 Quick Start

### Installation (5 minutes)
```bash
# 1. Clone repository
git clone https://github.com/Dubzyy/vrhost-lab.git
cd vrhost-lab

# 2. Run installer
sudo bash install.sh

# 3. Access the platform
# Local: http://localhost:3000
# Remote: http://YOUR_SERVER_IP:3000
```

### What the Installer Does

- ✅ Installs Node.js, Python, KVM, QEMU, libvirt, ttyd
- ✅ Creates Python virtual environment
- ✅ Builds React frontend
- ✅ Configures systemd services (vrhost-api, vrhost-web)
- ✅ Sets up networking
- ✅ Starts the platform automatically

### First Router
```bash
# 1. Download Juniper vSRX image (separately)
# Place in: /var/lib/libvirt/images/juniper/

# 2. Create router
sudo mkjuniper r1

# 3. Access via web interface
# Click "Console" button to access router CLI
```

---

## 📖 Documentation

- 📗 [**Router Setup Guide**](docs/ROUTER_SETUP.md) - Creating and configuring routers
- 📙 [**API Documentation**](http://localhost:8000/docs) - Interactive API reference (when running)
- 📕 [**GitHub Wiki**](https://github.com/Dubzyy/vrhost-lab/wiki) - Additional guides and tips

**Coming Soon:**
- 📘 Installation Guide (detailed step-by-step)
- 📔 Troubleshooting Guide
- 📓 Architecture Documentation

---

## 🌐 Remote Access

### Method 1: SSH Tunnel (Simple)
```bash
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 user@your-server
```

Then access: `http://localhost:3000`

### Method 2: SSH + SOCKS Proxy (For Console)
```bash
ssh -D 8080 -L 3000:localhost:3000 -L 8000:localhost:8000 user@your-server
```

Configure browser SOCKS proxy: `localhost:8080`

### Method 3: Tailscale (Recommended)
```bash
# On server
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Access from anywhere
http://100.x.x.x:3000
```

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      Web Browser                             │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │   Topology   │  │   Console    │      │
│  │   (React)    │  │ (Cytoscape)  │  │    (ttyd)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │         HTTP/REST API + WebSocket   │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  RouterService  │  LabService  │  ConsoleService    │    │
│  │  StatsService   │  TopologyService                  │    │
│  └──────────┬───────────────┬──────────────┬───────────┘    │
└─────────────┼────────────────┼──────────────┼────────────────┘
              │                │              │
              ▼                ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    libvirt / KVM Layer                       │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Virtual Network (br0 bridge)                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  vSRX-1  │  │  vSRX-2  │  │  vSRX-3  │  │  vSRX-4  │    │
│  │ (4GB/2C) │  │ (4GB/2C) │  │ (4GB/2C) │  │ (4GB/2C) │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure
```
vrhost-lab/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main application entry
│   ├── models/                # Pydantic data models
│   │   ├── router.py
│   │   ├── lab.py
│   │   └── topology.py
│   └── services/              # Business logic
│       ├── router_service.py  # Router management
│       ├── lab_service.py     # Lab management
│       ├── stats_service.py   # Statistics
│       └── console_service.py # Web console (ttyd)
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.js            # Main component
│   │   ├── Topology.js       # Cytoscape topology
│   │   └── services/
│   │       └── api.js        # API client
│   ├── public/
│   └── package.json
│
├── scripts/                    # Helper scripts
│   ├── mkjuniper              # Create Juniper router
│   ├── mkcisco-router         # Create Cisco router (WIP)
│   ├── mkcisco-switch         # Create Cisco switch (WIP)
│   └── mkvm                   # Generic VM creation
│
├── docs/                       # Documentation
│   └── ROUTER_SETUP.md        # Router setup guide
│
├── install.sh                 # One-command installer
├── README.md                  # This file
└── LICENSE                    # MIT License
```

---

## 🗺️ Roadmap

### ✅ Phase 1: Core Platform (Complete)
- ✅ FastAPI backend with REST API
- ✅ React frontend with Tailwind CSS
- ✅ Juniper vSRX support
- ✅ Web console access (ttyd)
- ✅ Interactive topology view
- ✅ Multi-lab management
- ✅ One-command installer
- ✅ systemd service integration

### 🚧 Phase 2: Multi-Vendor Support (In Progress)
- ✅ Cisco IOSv router scripts created
- ✅ Cisco IOSvL2 switch scripts created
- 🔜 Cisco image integration testing
- 🔜 Backend API multi-vendor support
- 🔜 Frontend vendor badges/icons
- 🔜 Topology color-coding by vendor

### 🔮 Phase 3: Advanced Features (Planned)
- 🔜 Router snapshots and cloning
- 🔜 Configuration backup/restore
- 🔜 Lab templates (save/load topologies)
- 🔜 Network diagram export (PNG/SVG)
- 🔜 Automated lab provisioning
- 🔜 YAML-based lab definitions

### 🚀 Phase 4: Platform Enhancement (Future)
- 🔜 User authentication
- 🔜 Multi-user support
- 🔜 Role-based access control
- 🔜 Centralized logging (Graylog)
- 🔜 Metrics dashboard (Prometheus/Grafana)
- 🔜 API rate limiting
- 🔜 WebSocket for real-time updates

### 🌟 Phase 5: Additional Platforms (Future)
- 🔜 Arista vEOS support
- 🔜 Mikrotik CHR support
- 🔜 Nokia VSR support
- 🔜 VyOS support
- 🔜 Linux containers for hosts

---

## 🎓 Perfect For

- 📚 **Certification Studies** - JNCIS-SP, JNCIA, CCNA, CCNP
- 🔬 **Network Testing** - Protocol testing, feature validation
- 🏫 **Training Labs** - Teaching network concepts
- 🔧 **Development** - Network automation development
- 📊 **Research** - Network behavior analysis

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

# Restart services
sudo systemctl restart vrhost-api vrhost-web
```

### Router Won't Boot
```bash
# Check libvirt
virsh list --all
virsh dominfo router-name

# Check KVM support
sudo kvm-ok

# View VM logs
sudo journalctl -t libvirt -f
```

### Console Not Working
```bash
# Check ttyd installation
which ttyd

# Check console sessions
ps aux | grep ttyd

# Test manual connection
virsh console router-name
```

### Frontend Not Loading
```bash
# Check service
sudo systemctl status vrhost-web

# Rebuild frontend
cd /opt/vrhost-lab/frontend
npm run build
sudo systemctl restart vrhost-web
```

**For more help**, open an issue on [GitHub Issues](https://github.com/Dubzyy/vrhost-lab/issues).

---

## 🤝 Contributing

Contributions are welcome! Whether it's:

- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🔧 Code contributions

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Backend development
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
npm install
npm start  # Runs on port 3000
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Inspired by**: EVE-NG and GNS3 - the pioneers of network lab virtualization
- **Built for**: Network engineers studying for Juniper and Cisco certifications
- **Powered by**: 
  - [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
  - [React](https://reactjs.org/) - UI library
  - [Cytoscape.js](https://js.cytoscape.org/) - Graph visualization
  - [ttyd](https://github.com/tsl0922/ttyd) - Web terminal
  - [libvirt](https://libvirt.org/) - Virtualization API

---

## 📧 Contact & Support

**Author**: Hunter Wilson

- 🐙 GitHub: [@Dubzyy](https://github.com/Dubzyy)
- 💼 LinkedIn: [Hunter Wilson](https://linkedin.com/in/hunter-wilsonit)
- 🌐 Portfolio: [https://portfolio.vrhost.org](https://portfolio.vrhost.org)

**Project Links**:
- 🔗 Repository: [https://github.com/Dubzyy/vrhost-lab](https://github.com/Dubzyy/vrhost-lab)
- 🐛 Issues: [https://github.com/Dubzyy/vrhost-lab/issues](https://github.com/Dubzyy/vrhost-lab/issues)
- 💬 Discussions: [https://github.com/Dubzyy/vrhost-lab/discussions](https://github.com/Dubzyy/vrhost-lab/discussions)

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

**Built with ❤️ for the network engineering community**

[![GitHub stars](https://img.shields.io/github/stars/Dubzyy/vrhost-lab?style=social)](https://github.com/Dubzyy/vrhost-lab)
[![GitHub forks](https://img.shields.io/github/forks/Dubzyy/vrhost-lab?style=social)](https://github.com/Dubzyy/vrhost-lab/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/Dubzyy/vrhost-lab?style=social)](https://github.com/Dubzyy/vrhost-lab)

[🚀 Get Started](#-quick-start) • [📖 Documentation](#-documentation) • [🐛 Report Bug](https://github.com/Dubzyy/vrhost-lab/issues) • [💡 Request Feature](https://github.com/Dubzyy/vrhost-lab/issues)

</div>
