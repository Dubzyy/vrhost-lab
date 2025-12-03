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
