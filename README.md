# VRHost Lab

**Lightweight network lab platform built by a NOC engineer for NOC engineers**

VRHost Lab is a modern, web-based network lab management platform that simplifies virtual router deployment and management. Built with Python FastAPI and React, it provides an intuitive interface for creating and managing network lab environments.

![VRHost Lab Dashboard](docs/screenshot-dashboard.png)

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

## 🚀 Quick Start

### Prerequisites
- Ubuntu 22.04+ (or similar Linux)
- KVM/QEMU with libvirt
- Python 3.10+
- Node.js 20+

### Backend Installation
```bash
# Clone the repository
git clone https://github.com/Dubzyy/vrhost-lab.git
cd vrhost-lab

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn[standard] libvirt-python pydantic websockets python-multipart

# Start the API server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: `http://localhost:8000`  
API Documentation: `http://localhost:8000/docs`

### Frontend Installation
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: `http://localhost:3000`

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
└── topologies/              # Saved topologies
```

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

**List all labs:**
```bash
curl http://localhost:8000/api/labs
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

### Bulk Operations
- `POST /api/routers/bulk/start-all` - Start all routers
- `POST /api/routers/bulk/stop-all` - Stop all routers

Full API documentation available at `/docs` endpoint (Swagger UI)

## 🛠️ Tech Stack

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

## 🎨 Screenshots

*Coming soon - add screenshots of:*
- Dashboard with multiple labs
- Router management interface
- Lab creation modal
- System statistics view

## 🗺️ Roadmap

- [ ] Visual topology builder
- [ ] Multi-host support (manage multiple servers)
- [ ] Console access via web terminal
- [ ] Network configuration templates
- [ ] Automated lab provisioning
- [ ] RBAC (Role-Based Access Control)
- [ ] Lab sharing and export
- [ ] Support for additional platforms (Cisco, Arista, etc.)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

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

## 📊 Stats

- **26+ API endpoints**
- **Full-stack application**
- **Production-ready**
- **Open source**

---

**Built with ❤️ by a NOC engineer who wanted better lab tooling**
