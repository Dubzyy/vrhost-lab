# VRHost Lab

A lightweight, web-based network lab platform for managing virtual routers. Built with FastAPI and React, designed for network engineers studying for certifications like JNCIS-SP.

![VRHost Lab Dashboard](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-18.3-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **🚀 One-Command Installation** - Complete setup in under 5 minutes
- **🌐 Web-Based Management** - Clean, modern interface accessible from anywhere
- **💻 Integrated Web Console** - Browser-based terminal access to routers using ttyd
- **📊 Interactive Topology View** - Visual network diagrams with drag-and-drop positioning
- **🔄 Real-Time Monitoring** - Live router states and system resource tracking
- **🏗️ Multi-Lab Support** - Organize routers into isolated lab environments
- **⚡ Quick Actions** - Start/Stop/Restart routers with optimistic UI updates
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **🔐 Remote Access Ready** - SSH tunnel + SOCKS proxy support for remote management

## 🎯 Key Features

### Web Console Access
Direct browser-based terminal access to router consoles. No need for separate SSH clients - click "Console" and you're in!

- Token-based session management
- Multiple concurrent console sessions
- Secure ttyd integration
- Works through SSH tunnels and SOCKS proxies

### Interactive Topology Visualization
Beautiful network topology view powered by Cytoscape.js:

- Real-time state visualization (color-coded by status)
- Drag-and-drop router positioning
- Multiple layout algorithms (Circle, Grid)
- Click nodes for detailed router information
- Auto-refresh with live updates

### Lab Management
Organize your network labs efficiently:

- Group routers by lab/project
- Start/stop entire labs with one click
- Track running vs total routers per lab
- Filter routers by lab

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- libvirt for KVM/QEMU management
- ttyd for web-based terminal access
- uvicorn ASGI server

**Frontend:**
- React 18.3
- Tailwind CSS
- Cytoscape.js for topology visualization
- Axios for API communication

**Infrastructure:**
- KVM/QEMU virtualization
- systemd service management
- Juniper vSRX routers

## 📋 Prerequisites

- Ubuntu 22.04 LTS or newer
- Root/sudo access
- KVM-enabled host (CPU virtualization support)
- 8GB+ RAM recommended
- 50GB+ free disk space
- Juniper vSRX image (download separately)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Dubzyy/vrhost-lab.git
cd vrhost-lab
```

### 2. Run Installer
```bash
sudo bash install.sh
```

The installer will:
- ✅ Install all dependencies (Node.js, Python, KVM, ttyd)
- ✅ Create Python virtual environment
- ✅ Build React frontend
- ✅ Configure systemd services
- ✅ Set up networking
- ✅ Start the platform

### 3. Access the Platform

**Local Access:**
```
http://10.10.50.1:3000
```

**API Documentation:**
```
http://10.10.50.1:8000/docs
```

### 4. Create Your First Router

See [Router Setup Guide](docs/ROUTER_SETUP.md) for detailed instructions on:
- Downloading and configuring vSRX images
- Using the `mkjuniper` script
- Creating routers through the web interface

## 🌐 Remote Access

### SSH Tunnel (Recommended)
```bash
ssh -L 3000:100.77.52.108:3000 -L 8000:100.77.52.108:8000 your-jump-host
```

### SSH Tunnel + SOCKS Proxy (For Console Access)
```bash
ssh -D 8080 -L 3000:100.77.52.108:3000 -L 8000:100.77.52.108:8000 your-jump-host
```

Then configure your browser to use SOCKS proxy `localhost:8080`.

## 📖 Usage

### Creating a Lab

1. Click **"+ New Lab"**
2. Enter lab name (e.g., `jncis-sp-lab`)
3. Add description
4. Click **"Create Lab"**

### Creating a Router

1. Click **"+ New Router"**
2. Fill in details:
   - Name: `jncis-sp-r1` (tip: use lab prefix for grouping)
   - IP Address: `10.10.50.13`
   - RAM: 4GB (minimum for vSRX)
   - vCPUs: 2
3. Click **"Create Router"**
4. Wait ~90 seconds for boot

### Using Web Console

1. Ensure router is **running** (green status)
2. Click **"Console"** button
3. New window opens with terminal
4. Login: `root` (no password initially)

### Viewing Topology

1. Click **"🌐 Topology View"** tab
2. Drag routers to reposition
3. Click router nodes for details
4. Use layout buttons:
   - **Circle Layout** - Arrange in circle
   - **Grid Layout** - Arrange in grid
   - **Fit View** - Center and zoom to fit

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Dashboard   │  │   Topology   │  │   Console    │  │
│  │   (React)    │  │ (Cytoscape)  │  │    (ttyd)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ├──────────────────┴──────────────────┘
          │         HTTP/WebSocket
          ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  RouterService  │  LabService  │  ConsoleService │   │
│  └──────────┬────────────┬────────────┬─────────────┘   │
└─────────────┼─────────────┼────────────┼─────────────────┘
              │             │            │
              ▼             ▼            ▼
┌─────────────────────────────────────────────────────────┐
│                    libvirt / KVM                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  vSRX-1  │  │  vSRX-2  │  │  vSRX-3  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

## 📂 Project Structure
```
vrhost-lab/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── models/                    # Pydantic models
│   │   ├── router.py
│   │   ├── lab.py
│   │   └── topology.py
│   └── services/                  # Business logic
│       ├── router_service.py
│       ├── lab_service.py
│       ├── stats_service.py
│       └── console_service.py     # Web console management
├── frontend/
│   ├── src/
│   │   ├── App.js                 # Main React component
│   │   ├── Topology.js            # Topology visualization
│   │   └── services/
│   │       └── api.js             # API client
│   ├── public/
│   └── package.json
├── scripts/
│   ├── mkjuniper                  # Router creation script
│   └── mkvm                       # Generic VM creation
├── docs/
│   └── ROUTER_SETUP.md            # Router setup guide
└── install.sh                     # One-command installer
```

## 🔧 Manual Installation (Advanced)

If you prefer manual setup or need to customize:

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start  # Development
npm run build  # Production
```

### Install ttyd
```bash
sudo apt update
sudo apt install -y ttyd
```

## 🐛 Troubleshooting

### Routers Won't Start
```bash
# Check libvirt connection
virsh list --all

# Check router status
virsh dominfo router-name

# View logs
sudo journalctl -u vrhost-api -n 50
```

### Console Won't Open
```bash
# Check ttyd is installed
ttyd --version

# Check console sessions
ps aux | grep ttyd

# Check API logs
sudo journalctl -u vrhost-api | grep console
```

### Frontend Not Loading
```bash
# Check web service
sudo systemctl status vrhost-web

# Rebuild frontend
cd /opt/vrhost-lab/frontend
npm run build
sudo systemctl restart vrhost-web
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by EVE-NG and GNS3
- Built for network engineers studying for Juniper certifications
- Special thanks to the FastAPI, React, and Cytoscape.js communities

## 📧 Contact

Hunter Wilson - [@Dubzyy](https://github.com/Dubzyy)

Project Link: [https://github.com/Dubzyy/vrhost-lab](https://github.com/Dubzyy/vrhost-lab)

---

**⭐ Star this repo if you find it useful!**
