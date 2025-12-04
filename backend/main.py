from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import libvirt

from backend.models.router import RouterCreate, RouterInfo
from backend.services.router_service import RouterService
from backend.services.stats_service import StatsService
from backend.services.console_service import ConsoleService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage libvirt connection lifecycle"""
    # Startup
    try:
        app.state.libvirt_conn = libvirt.open('qemu:///system')
        app.state.router_service = RouterService(app.state.libvirt_conn)
        app.state.stats_service = StatsService(app.state.libvirt_conn)
        app.state.lab_service = LabService()
        app.state.console_service = ConsoleService()
        print("✓ Connected to libvirt")
    except Exception as e:
        print(f"✗ Failed to connect to libvirt: {e}")
    
    yield
    
    # Shutdown
    # Cleanup console sessions
    if hasattr(app.state, 'console_service'):
        app.state.console_service.cleanup_old_sessions()
    
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

# Lab Management
from backend.models.lab import LabCreate, LabInfo
from backend.services.lab_service import LabService

# Initialize lab service in lifespan (add this line after router_service initialization)
# Add: app.state.lab_service = LabService()

@app.get("/api/labs", response_model=List[dict])
async def list_labs():
    """List all labs"""
    return app.state.lab_service.list_labs(app.state.router_service)

@app.post("/api/labs")
async def create_lab(lab: LabCreate):
    """Create a new lab"""
    result = app.state.lab_service.create_lab(lab.name, lab.description)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.get("/api/labs/{name}")
async def get_lab(name: str):
    """Get lab details"""
    result = app.state.lab_service.get_lab(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.delete("/api/labs/{name}")
async def delete_lab(name: str):
    """Delete a lab"""
    result = app.state.lab_service.delete_lab(name)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404, detail=result["message"])

@app.get("/api/labs/{name}/routers")
async def get_lab_routers(name: str):
    """Get all routers in a lab"""
    routers = app.state.lab_service.get_lab_routers(name, app.state.router_service)
    return {"lab": name, "routers": routers, "count": len(routers)}

@app.post("/api/labs/{name}/start")
async def start_lab(name: str):
    """Start all routers in a lab"""
    routers = app.state.lab_service.get_lab_routers(name, app.state.router_service)
    started = []
    failed = []
    
    for router in routers:
        if router['state'] != 'running':
            result = app.state.router_service.start_router(router['name'])
            if result['success']:
                started.append(router['name'])
            else:
                failed.append({"name": router['name'], "error": result['message']})
    
    return {"success": True, "started": started, "failed": failed}

@app.post("/api/labs/{name}/stop")
async def stop_lab(name: str, force: bool = False):
    """Stop all routers in a lab"""
    routers = app.state.lab_service.get_lab_routers(name, app.state.router_service)
    stopped = []
    failed = []
    
    for router in routers:
        if router['state'] == 'running':
            result = app.state.router_service.stop_router(router['name'], force)
            if result['success']:
                stopped.append(router['name'])
            else:
                failed.append({"name": router['name'], "error": result['message']})
    
    return {"success": True, "stopped": stopped, "failed": failed}


# ============================================
# Console Management
# ============================================

@app.post("/api/routers/{name}/console/session")
async def create_console_session(name: str):
    """Create a web console session for a router"""
    try:
        # Check if router exists
        router = app.state.router_service.get_router_details(name)
        if "error" in router:
            raise HTTPException(status_code=404, detail="Router not found")
        
        # Create console session
        session = app.state.console_service.create_console_session(name)
        
        return {
            "success": True,
            "token": session['token'],
            "port": session['port']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/console/{token}")
async def get_console_session(token: str):
    """Get console session info"""
    session = app.state.console_service.get_session(token)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "router_name": session['router_name'],
        "port": session['port']
    }

@app.delete("/api/console/{token}")
async def close_console_session(token: str):
    """Close a console session"""
    app.state.console_service.close_session(token)
    return {"success": True}
