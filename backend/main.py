from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import libvirt

from backend.models.router import RouterCreate, RouterInfo
from backend.services.router_service import RouterService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage libvirt connection lifecycle"""
    # Startup
    try:
        app.state.libvirt_conn = libvirt.open('qemu:///system')
        app.state.router_service = RouterService(app.state.libvirt_conn)
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
