from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import libvirt

from backend.models.router import RouterCreate, RouterInfo
from backend.services.router_service import RouterService
from backend.services.stats_service import StatsService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage libvirt connection lifecycle"""
    # Startup
    try:
        app.state.libvirt_conn = libvirt.open('qemu:///system')
        app.state.router_service = RouterService(app.state.libvirt_conn)
        app.state.stats_service = StatsService(app.state.libvirt_conn)
        print("✓ Connected to libvirt")
    except Exception as e:
        print(f"✗ Failed to connect to libvirt: {e}")
    
    yield
    
    # Shutdown
    if hasattr(app.state, 'libvirt_conn'):
        app.state.libvirt_conn.close()
        print("✓ Disconnected from libvirt")

app = FastAPI(
    title="VRHost Lab API",
    description="Lightweight network lab platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "VRHost Lab API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = app.state.libvirt_conn
        domains = conn.listAllDomains()
        return {
            "status": "healthy",
            "libvirt_connected": True,
            "total_vms": len(domains)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/api/routers", response_model=dict)
async def list_routers():
    """List all routers"""
    try:
        routers = app.state.router_service.list_routers()
        return {
            "routers": routers,
            "count": len(routers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/routers")
async def create_router(router: RouterCreate):
    """Create a new router"""
    try:
        result = app.state.router_service.create_router(
            name=router.name,
            ip=router.ip,
            router_type=router.router_type,
            ram=router.ram_gb,
            vcpus=router.vcpus
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/routers/{name}")
async def delete_router(name: str):
    """Delete a router"""
    try:
        result = app.state.router_service.delete_router(name)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/routers/{name}/console")
async def get_console_info(name: str):
    """Get console access information for a router"""
    return {
        "name": name,
        "ssh_command": f"ssh root@{name}",
        "virsh_command": f"virsh console {name}",
        "note": "Use virsh console from host system"
    }

@app.post("/api/routers/{name}/start")
async def start_router(name: str):
    """Start a stopped router"""
    result = app.state.router_service.start_router(name)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.post("/api/routers/{name}/stop")
async def stop_router(name: str, force: bool = False):
    """Stop a running router"""
    result = app.state.router_service.stop_router(name, force)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.post("/api/routers/{name}/restart")
async def restart_router(name: str):
    """Restart a router"""
    result = app.state.router_service.restart_router(name)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.get("/api/routers/{name}")
async def get_router_details(name: str):
    """Get detailed information about a router"""
    result = app.state.router_service.get_router_details(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/api/routers/bulk/start-all")
async def start_all_routers():
    """Start all stopped routers"""
    result = app.state.router_service.start_all_routers()
    return result

@app.post("/api/routers/bulk/stop-all")
async def stop_all_routers(force: bool = False):
    """Stop all running routers"""
    result = app.state.router_service.stop_all_routers(force)
    return result

@app.get("/api/stats/system")
async def get_system_stats():
    """Get overall system statistics"""
    return app.state.stats_service.get_system_stats()

@app.get("/api/stats/routers/{name}")
async def get_router_stats(name: str):
    """Get real-time statistics for a specific router"""
    result = app.state.stats_service.get_router_stats(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# Topology Management
from backend.models.topology import Topology, TopologyInfo
from backend.services.topology_service import TopologyService

# Initialize topology service (add near other service initializations in lifespan)
topology_service = TopologyService()

@app.get("/api/topologies", response_model=List[dict])
async def list_topologies():
    """List all saved topologies"""
    return topology_service.list_topologies()

@app.post("/api/topologies")
async def save_topology(topology: Topology):
    """Save current lab topology"""
    result = topology_service.save_topology(
        name=topology.name,
        description=topology.description,
        routers=[r.dict() for r in topology.routers]
    )
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.get("/api/topologies/{name}")
async def load_topology(name: str):
    """Load a saved topology"""
    result = topology_service.load_topology(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.delete("/api/topologies/{name}")
async def delete_topology(name: str):
    """Delete a saved topology"""
    result = topology_service.delete_topology(name)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404, detail=result["message"])
