import subprocess
import libvirt
from typing import List, Dict

class RouterService:
    def __init__(self, conn: libvirt.virConnect):
        self.conn = conn
    
    def list_routers(self) -> List[Dict]:
        """List all routers/VMs"""
        routers = []
        domains = self.conn.listAllDomains()
        
        for domain in domains:
            info = domain.info()
            routers.append({
                "name": domain.name(),
                "state": self._get_state_name(info[0]),
                "memory_mb": int(info[1] / 1024),
                "vcpus": info[3],
                "id": domain.ID() if domain.ID() != -1 else None
            })
        
        return routers
    
    def create_router(self, name: str, ip: str, router_type: str, ram: int, vcpus: int) -> Dict:
        """Create router using mkjuniper script"""
        cmd = ["mkjuniper", name, ip, router_type, str(ram), str(vcpus)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=True
            )
            
            return {
                "success": True,
                "message": f"Router {name} created successfully",
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "message": f"Failed to create router: {e.stderr}",
                "error": e.stderr
            }
    
    def delete_router(self, name: str) -> Dict:
        """Delete router using mkjuniper script"""
        cmd = ["mkjuniper", "delete", name]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "success": True,
                "message": f"Router {name} deleted successfully"
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "message": f"Failed to delete router: {e.stderr}",
                "error": e.stderr
            }
    
    @staticmethod
    def _get_state_name(state_code: int) -> str:
        """Convert libvirt state code to name"""
        states = {
            0: "nostate", 1: "running", 2: "blocked", 3: "paused",
            4: "shutdown", 5: "shutoff", 6: "crashed", 7: "suspended"
        }
        return states.get(state_code, "unknown")

    def start_router(self, name: str) -> Dict:
        """Start a stopped router"""
        try:
            domain = self.conn.lookupByName(name)
            if domain.isActive():
                return {"success": False, "message": f"Router {name} is already running"}
            
            domain.create()
            return {"success": True, "message": f"Router {name} started"}
        except libvirt.libvirtError as e:
            return {"success": False, "message": str(e)}
    
    def stop_router(self, name: str, force: bool = False) -> Dict:
        """Stop a running router"""
        try:
            domain = self.conn.lookupByName(name)
            if not domain.isActive():
                return {"success": False, "message": f"Router {name} is already stopped"}
            
            if force:
                domain.destroy()  # Force stop
            else:
                domain.shutdown()  # Graceful shutdown
            
            return {"success": True, "message": f"Router {name} stopped"}
        except libvirt.libvirtError as e:
            return {"success": False, "message": str(e)}
    
    def restart_router(self, name: str) -> Dict:
        """Restart a router"""
        try:
            domain = self.conn.lookupByName(name)
            if not domain.isActive():
                return {"success": False, "message": f"Router {name} is not running"}
            
            domain.reboot()
            return {"success": True, "message": f"Router {name} restarting"}
        except libvirt.libvirtError as e:
            return {"success": False, "message": str(e)}
    
    def get_router_details(self, name: str) -> Dict:
        """Get detailed info about a router"""
        try:
            domain = self.conn.lookupByName(name)
            info = domain.info()
            
            return {
                "name": name,
                "state": self._get_state_name(info[0]),
                "max_memory_mb": int(info[1] / 1024),
                "memory_mb": int(info[2] / 1024),
                "vcpus": info[3],
                "cpu_time_ns": info[4],
                "id": domain.ID() if domain.ID() != -1 else None,
                "uuid": domain.UUIDString(),
                "autostart": domain.autostart() == 1
            }
        except libvirt.libvirtError as e:
            return {"error": str(e)}

    def start_all_routers(self) -> Dict:
        """Start all stopped routers"""
        domains = self.conn.listAllDomains()
        started = []
        failed = []
        
        for domain in domains:
            if not domain.isActive():
                try:
                    domain.create()
                    started.append(domain.name())
                except Exception as e:
                    failed.append({"name": domain.name(), "error": str(e)})
        
        return {
            "success": True,
            "started": started,
            "failed": failed,
            "count": len(started)
        }
    
    def stop_all_routers(self, force: bool = False) -> Dict:
        """Stop all running routers"""
        domains = self.conn.listAllDomains()
        stopped = []
        failed = []
        
        for domain in domains:
            if domain.isActive():
                try:
                    if force:
                        domain.destroy()
                    else:
                        domain.shutdown()
                    stopped.append(domain.name())
                except Exception as e:
                    failed.append({"name": domain.name(), "error": str(e)})
        
        return {
            "success": True,
            "stopped": stopped,
            "failed": failed,
            "count": len(stopped)
        }
