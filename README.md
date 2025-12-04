# VRHost Lab

**Lightweight network lab platform built by a NOC engineer for NOC engineers**

VRHost Lab is a modern, web-based network lab management platform that simplifies virtual router deployment and management. Built with Python FastAPI and React, it provides an intuitive interface for creating and managing network lab environments.

## 🚀 Quick Install

**One-command installation on Ubuntu 22.04+:**
```bash
git clone https://github.com/Dubzyy/vrhost-lab.git
cd vrhost-lab
sudo ./install.sh
```

**That's it!** Installation takes ~5 minutes and includes:
- All dependencies (libvirt, Node.js, Python)
- Backend API + Frontend UI
- Systemd services (auto-start on boot)
- Production build

Then access at: `http://YOUR_SERVER_IP:3000`

📖 **[Full Installation Guide](INSTALL.md)** | 🔧 **[Manual Installation](#manual-installation)**

---

## ✨ Features

### Lab Management (EVE-NG Style)
- **Multi-Lab Support**: Create and manage multiple isolated lab environments
- **Lab Controls**: Start/stop all routers in a lab with one click
- **Lab Filtering**: View routers by lab or see all routers at once
- **Lab Templates**: Save and load lab topologies

### Router Management
- **Create Routers**: Deploy vSRX routers via web UI or API
- **Power Controls**: Start, stop, restart individual routers
- **Bulk Operations**: Start/stop all routers simultaneously
- **Real-time Status**: Live router state monitoring with auto-refresh

### System Monitoring
- **Resource Tracking**: Monitor memory, CPU, and disk usage
- **Live Statistics**: Real-time router stats and system health
- **Capacity Planning**: See available resources at a glance

### Modern Architecture
- **REST API**: 26+ endpoints for complete programmatic control
- **Real-time Updates**: Dashboard refreshes every 5 seconds
- **Beautiful UI**: Dark theme with responsive design
- **Fast**: Built on FastAPI for high performance

## 📊 Screenshots

![VRHost Lab Dashboard](https://via.placeholder.com/800x450/111827/10b981?text=Dashboard+Screenshot)

*Beautiful dark-themed interface with multi-lab support*

## 🎯 Usage

### Creating a Lab

1. Click **"+ New Lab"** in the dashboard
2. Enter lab name (e.g., `jncis-sp`)
3. Add description (optional)
4. Click **"Create Lab"**

### Adding Routers to a Lab

Routers are associated with labs via naming convention:
- Lab name: `jncis-sp`
- Router names: `jncis-sp-r1`, `jncis-sp-r2`, `jncis-sp-r3`

**Via Web UI:**
Click "+ New Router" button (coming soon)

**Via API:**
```bash
curl -X POST http://localhost:8000/api/routers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "jncis-sp-r1",
    "ip": "10.10.50.10",
    "router_type": "vsrx",
    "ram_gb": 4,
    "vcpus": 2
  }'
```

### Managing Labs

**Start all routers in a lab:**
```bash
curl -X POST http://localhost:8000/api/labs/jncis-sp/start
```

**Stop all routers in a lab:**
```bash
curl -X POST http://localhost:8000/api/labs/jncis-sp/stop
```

## 🔌 API Endpoints

### Router Management
- `GET /api/routers` - List all routers
- `POST /api/routers` - Create new router
- `GET /api/routers/{name}` - Get router details
- `DELETE /api/routers/{name}` - Delete router
- `POST /api/routers/{name}/start` - Start router
- `POST /api/routers/{name}/stop` - Stop router
- `POST /api/routers/{name}/restart` - Restart router

### Lab Management
- `GET /api/labs` - List all labs
- `POST /api/labs` - Create new lab
- `GET /api/labs/{name}` - Get lab details
- `DELETE /api/labs/{name}` - Delete lab
- `GET /api/labs/{name}/routers` - Get lab routers
- `POST /api/labs/{name}/start` - Start all routers in lab
- `POST /api/labs/{name}/stop` - Stop all routers in lab

### System Stats
- `GET /api/stats/system` - Get system statistics
- `GET /api/stats/routers/{name}` - Get router statistics

### Topology Management
- `GET /api/topologies` - List saved topologies
- `POST /api/topologies` - Save topology
- `GET /api/topologies/{name}` - Load topology
- `DELETE /api/topologies/{name}` - Delete topology

Full API documentation: `http://localhost:8000/docs`

## 🛠️ Management

### Service Commands
```bash
# Check status
systemctl status vrhost-api
systemctl status vrhost-web

# Restart services
systemctl restart vrhost-api
systemctl restart vrhost-web

# View logs
journalctl -u vrhost-api -f
journalctl -u vrhost-web -f
```

### Update VRHost Lab
```bash
cd /opt/vrhost-lab
sudo ./update.sh
```

### Uninstall
```bash
cd /opt/vrhost-lab
sudo ./uninstall.sh
```

## 📚 Architecture
```
vrhost-lab/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   │   ├── router.py
│   │   ├── topology.py
│   │   └── lab.py
│   └── services/            # Business logic
│       ├── router_service.py
│       ├── stats_service.py
│       ├── topology_service.py
│       └── lab_service.py
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   └── services/
│   │       └── api.js       # API client
│   └── package.json
├── labs/                    # Lab definitions
├── topologies/              # Saved topologies
├── install.sh               # Automated installer
├── update.sh                # Update script
└── uninstall.sh             # Uninstaller
```

## 🔧 Tech Stack

**Backend:**
- Python 3.10
- FastAPI
- libvirt-python
- Pydantic
- Uvicorn

**Frontend:**
- React 19
- Tailwind CSS 3
- Axios
- React Router

**Infrastructure:**
- KVM/QEMU
- libvirt
- vSRX (Juniper)

## 💻 Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

### Prerequisites
- Ubuntu 22.04+ (or similar Linux)
- KVM/QEMU with libvirt
- Python 3.10+
- Node.js 20+

### Backend Setup
```bash
# Clone repository
git clone https://github.com/Dubzyy/vrhost-lab.git
cd vrhost-lab

# Install system dependencies
sudo apt install -y libvirt-daemon-system libvirt-clients qemu-kvm \
    python3 python3-pip python3-venv python3-dev libvirt-dev pkg-config gcc

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install fastapi uvicorn[standard] libvirt-python pydantic websockets python-multipart

# Start API server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

For production deployment, see [INSTALL.md](INSTALL.md)
</details>

## 🗺️ Roadmap

- [ ] Visual topology builder with drag-and-drop
- [ ] Router creation via web UI (modal form)
- [ ] Web-based console access (noVNC/xterm.js)
- [ ] Multi-host support (manage multiple servers)
- [ ] Network configuration templates
- [ ] Automated lab provisioning from templates
- [ ] RBAC (Role-Based Access Control)
- [ ] Lab sharing and import/export
- [ ] Support for additional platforms (Cisco, Arista, etc.)
- [ ] Performance metrics and graphs
- [ ] Scheduled lab start/stop

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Hunter Wilson**
- GitHub: [@Dubzyy](https://github.com/Dubzyy)
- Email: admin@vrhost.org
- Website: [vrhost.org](https://vrhost.org)

## 🙏 Acknowledgments

- Built for the networking community
- Inspired by EVE-NG and GNS3
- Designed for simplicity and speed
- Thanks to all contributors and users

## 📊 Project Stats

- **26+ API endpoints**
- **7 commits** (and growing!)
- **Full-stack application**
- **Production-ready**
- **Open source MIT**
- **Active development**

## ⭐ Star History

If you find VRHost Lab useful, please consider giving it a star on GitHub!

---

**Built with ❤️ by a NOC engineer who wanted better lab tooling**

**[Get Started →](INSTALL.md)** | **[API Docs →](http://localhost:8000/docs)** | **[Report Issues →](https://github.com/Dubzyy/vrhost-lab/issues)**

## 📦 Router Image Setup

Before using VRHost Lab, you need to provide a vSRX router image.

**See [Router Setup Guide](docs/ROUTER_SETUP.md) for:**
- Where to download vSRX image
- How to install it
- mkjuniper script usage
- Requirements and troubleshooting

