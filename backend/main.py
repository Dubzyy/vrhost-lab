from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import libvirt

from backend.models.router import RouterCreate, RouterInfo
from backend.models.topology import Topology, TopologyInfo
from backend.models.lab import LabCreate, LabInfo
from backend.models.link import Link, LinkCreate
from backend.services.router_service import RouterService
from backend.services.stats_service import StatsService
from backend.services.console_service import ConsoleService
from backend.services.topology_service import TopologyService
from backend.services.lab_service import LabService
from backend.services.link_service import LinkService

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
        app.state.topology_service = TopologyService()
        app.state.link_service = LinkService()
        print("✓ Connected to libvirt")
        print("✓ Link service initialized")
    except Exception as e:
        print(f"✗ Failed to connect to libvirt: {e}")

    yield

    # Shutdown
    # Cleanup console sessions
    if hasattr(app.state, 'console_service'):
        app.state.console_service.close_all_sessions()

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
async def health_check(request: Request):
    """Health check endpoint"""
    try:
        conn = request.app.state.libvirt_conn
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

# ============================================
# Router Management
# ============================================

@app.get("/api/routers", response_model=dict)
async def list_routers(request: Request):
    """List all routers"""
    try:
        routers = request.app.state.router_service.list_routers()
        return {
            "routers": routers,
            "count": len(routers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/routers")
async def create_router(router: RouterCreate, request: Request):
    """Create a new router"""
    try:
        result = request.app.state.router_service.create_router(
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
async def delete_router(name: str, request: Request):
    """Delete a router"""
    try:
        # Delete associated links first
        deleted_links = request.app.state.link_service.delete_router_links(name)

        result = request.app.state.router_service.delete_router(name)

        if result["success"]:
            result["deleted_links"] = deleted_links
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
async def start_router(name: str, request: Request):
    """Start a stopped router"""
    result = request.app.state.router_service.start_router(name)
    if result["success"]:
        # Update link status - PASS router_service to check both routers
        request.app.state.link_service.update_links_for_router(
            name, "running", request.app.state.router_service
        )
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.post("/api/routers/{name}/stop")
async def stop_router(name: str, force: bool = False, request: Request = None):
    """Stop a running router"""
    result = request.app.state.router_service.stop_router(name, force)
    if result["success"]:
        # Update link status - PASS router_service to check both routers
        request.app.state.link_service.update_links_for_router(
            name, "stopped", request.app.state.router_service
        )
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.post("/api/routers/{name}/restart")
async def restart_router(name: str, request: Request):
    """Restart a router"""
    result = request.app.state.router_service.restart_router(name)
    if result["success"]:
        # Update link status - PASS router_service to check both routers
        request.app.state.link_service.update_links_for_router(
            name, "running", request.app.state.router_service
        )
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.get("/api/routers/{name}")
async def get_router_details(name: str, request: Request):
    """Get detailed information about a router"""
    result = request.app.state.router_service.get_router_details(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # Add links to router details
    links = request.app.state.link_service.get_router_links(name)
    result["links"] = links

    return result

@app.post("/api/routers/bulk/start-all")
async def start_all_routers(request: Request):
    """Start all stopped routers"""
    result = request.app.state.router_service.start_all_routers()
    return result

@app.post("/api/routers/bulk/stop-all")
async def stop_all_routers(force: bool = False, request: Request = None):
    """Stop all running routers"""
    result = request.app.state.router_service.stop_all_routers(force)
    return result

# ============================================
# Link Management
# ============================================

@app.get("/api/links")
async def list_links(lab: str = None, request: Request = None):
    """Get all network links, optionally filtered by lab"""
    try:
        links = request.app.state.link_service.list_links(lab=lab)
        return {
            "links": links,
            "count": len(links)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/links")
async def create_link(link: LinkCreate, request: Request):
    """Create a new network link between two routers"""
    try:
        # PASS router_service to check initial status of both routers
        result = request.app.state.link_service.create_link(
            link, request.app.state.router_service
        )

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/links/{link_id}")
async def delete_link(link_id: str, request: Request):
    """Delete a network link"""
    try:
        result = request.app.state.link_service.delete_link(link_id)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/links/{link_id}")
async def get_link(link_id: str, request: Request):
    """Get details of a specific link"""
    link = request.app.state.link_service.get_link(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link.dict()

@app.get("/api/routers/{name}/links")
async def get_router_links(name: str, request: Request):
    """Get all links connected to a specific router"""
    links = request.app.state.link_service.get_router_links(name)
    return {
        "router": name,
        "links": links,
        "count": len(links)
    }

# ============================================
# Statistics
# ============================================

@app.get("/api/stats")
async def get_stats(request: Request):
    """Get simplified system statistics for dashboard"""
    system_stats = request.app.state.stats_service.get_system_stats()

    # Calculate percentages
    memory_percent = 0
    if system_stats.get('resources'):
        memory_used = system_stats['resources']['memory_used_mb']
        memory_total = system_stats['resources']['memory_total_mb']
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0

    cpu_percent = system_stats.get('disk', {}).get('used_percent', 0)

    return {
        "running_routers": system_stats.get('vms', {}).get('running', 0),
        "total_routers": system_stats.get('vms', {}).get('total', 0),
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent
    }

@app.get("/api/stats/system")
async def get_system_stats(request: Request):
    """Get overall system statistics"""
    return request.app.state.stats_service.get_system_stats()

@app.get("/api/stats/routers/{name}")
async def get_router_stats(name: str, request: Request):
    """Get real-time statistics for a specific router"""
    result = request.app.state.stats_service.get_router_stats(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# ============================================
# Topology Management
# ============================================

@app.get("/api/topologies", response_model=List[dict])
async def list_topologies(request: Request):
    """List all saved topologies"""
    return request.app.state.topology_service.list_topologies()

@app.post("/api/topologies")
async def save_topology(topology: Topology, request: Request):
    """Save current lab topology"""
    result = request.app.state.topology_service.save_topology(
        name=topology.name,
        description=topology.description,
        routers=[r.dict() for r in topology.routers]
    )

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.get("/api/topologies/{name}")
async def load_topology(name: str, request: Request):
    """Load a saved topology"""
    result = request.app.state.topology_service.load_topology(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.delete("/api/topologies/{name}")
async def delete_topology(name: str, request: Request):
    """Delete a saved topology"""
    result = request.app.state.topology_service.delete_topology(name)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404, detail=result["message"])

# ============================================
# Lab Management
# ============================================

@app.get("/api/labs", response_model=List[dict])
async def list_labs(request: Request):
    """List all labs"""
    return request.app.state.lab_service.list_labs(request.app.state.router_service)

@app.post("/api/labs")
async def create_lab(lab: LabCreate, request: Request):
    """Create a new lab"""
    result = request.app.state.lab_service.create_lab(lab.name, lab.description)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.get("/api/labs/{name}")
async def get_lab(name: str, request: Request):
    """Get lab details"""
    result = request.app.state.lab_service.get_lab(name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.delete("/api/labs/{name}")
async def delete_lab(name: str, request: Request):
    """Delete a lab"""
    result = request.app.state.lab_service.delete_lab(name)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404, detail=result["message"])

@app.get("/api/labs/{name}/routers")
async def get_lab_routers(name: str, request: Request):
    """Get all routers in a lab"""
    routers = request.app.state.lab_service.get_lab_routers(name, request.app.state.router_service)
    return {"lab": name, "routers": routers, "count": len(routers)}

@app.post("/api/labs/{name}/start")
async def start_lab(name: str, request: Request):
    """Start all routers in a lab"""
    routers = request.app.state.lab_service.get_lab_routers(name, request.app.state.router_service)
    started = []
    failed = []

    for router in routers:
        if router['state'] != 'running':
            result = request.app.state.router_service.start_router(router['name'])
            if result['success']:
                started.append(router['name'])
                # Update link status - PASS router_service to check both routers
                request.app.state.link_service.update_links_for_router(
                    router['name'], "running", request.app.state.router_service
                )
            else:
                failed.append({"name": router['name'], "error": result['message']})

    return {"success": True, "started": started, "failed": failed}

@app.post("/api/labs/{name}/stop")
async def stop_lab(name: str, force: bool = False, request: Request = None):
    """Stop all routers in a lab"""
    routers = request.app.state.lab_service.get_lab_routers(name, request.app.state.router_service)
    stopped = []
    failed = []

    for router in routers:
        if router['state'] == 'running':
            result = request.app.state.router_service.stop_router(router['name'], force)
            if result['success']:
                stopped.append(router['name'])
                # Update link status - PASS router_service to check both routers
                request.app.state.link_service.update_links_for_router(
                    router['name'], "stopped", request.app.state.router_service
                )
            else:
                failed.append({"name": router['name'], "error": result['message']})

    return {"success": True, "stopped": stopped, "failed": failed}

# ============================================
# Console Management
# ============================================

@app.post("/api/routers/{name}/console/session")
async def create_console_session(name: str, request: Request):
    """Create a web console session for a router"""
    try:
        # Check if router exists
        router = request.app.state.router_service.get_router_details(name)
        if "error" in router:
            raise HTTPException(status_code=404, detail="Router not found")

        # Create console session
        session = request.app.state.console_service.create_session(name)

        return {
            "success": True,
            "token": session['token'],
            "port": session['port']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/console/{token}")
async def get_console_session(token: str, request: Request):
    """Get console session info"""
    session = request.app.state.console_service.get_session(token)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return {
        "router_name": session['router_name'],
        "port": session['port']
    }

@app.delete("/api/console/{token}")
async def close_console_session(token: str, request: Request):
    """Close a console session"""
    request.app.state.console_service.close_session(token)
    return {"success": True}
