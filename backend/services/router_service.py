import subprocess
import libvirt
from typing import List, Dict

class RouterService:
    def __init__(self, conn: libvirt.virConnect):
        self.conn = conn

    def get_router_type(self, domain) -> str:
        """Detect router/switch type from domain XML or name"""
        try:
            xml = domain.XMLDesc()
            name = domain.name()

            # Check for switches first
            if 'viosl2' in xml.lower() or name.startswith('sw') or 'iosvl2' in name.lower():
                return 'cisco-switch'
            elif 'vjunos-switch' in xml.lower() or 'vqfx' in xml.lower():
                return 'juniper-switch'
            
            # Then check for routers
            if 'csr1000v' in xml.lower():
                return 'cisco'
            elif 'vsrx' in xml.lower():
                return 'juniper'
            elif name.startswith('csr-') or 'cisco' in name.lower():
                return 'cisco'
            
            return 'juniper'  # Default to juniper
        except Exception:
            return 'juniper'

    def list_routers(self) -> List[Dict]:
        """List all routers/VMs with router type"""
        routers = []
        domains = self.conn.listAllDomains()

        for domain in domains:
            info = domain.info()
            router_type = self.get_router_type(domain)

            routers.append({
                "name": domain.name(),
                "state": self._get_state_name(info[0]),
                "memory_mb": int(info[1] / 1024),
                "vcpus": info[3],
                "id": domain.ID() if domain.ID() != -1 else None,
                "router_type": router_type
            })

        return routers

    def create_router(self, name: str, ip: str = None, router_type: str = "juniper",
                     ram: int = 4, vcpus: int = 2) -> Dict:
        """Create router or switch - supports multiple vendors and device types"""
        try:
            if router_type.lower() in ["juniper", "vsrx"]:
                # Juniper vSRX - use mkjuniper script
                cmd = ["mkjuniper", name]
            elif router_type.lower() in ["cisco", "csr1000v", "csr"]:
                # Cisco CSR1000v - use mkcsr1000v script
                cmd = ["mkcsr1000v", name]
            elif router_type.lower() in ["cisco-switch", "iosvl2", "viosl2"]:
                # Cisco IOSvL2 - use mkviosl2 script
                cmd = ["mkviosl2", name]
            elif router_type.lower() in ["juniper-switch", "vqfx"]:
                # Juniper vQFX - use mkvqfx script (to be implemented)
                cmd = ["mkvqfx", name]
            else:
                return {
                    "success": False,
                    "message": f"Unsupported router type: {router_type}. Use 'juniper', 'cisco', 'cisco-switch', or 'juniper-switch'"
                }

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=True
            )

            return {
                "success": True,
                "message": f"{router_type.capitalize()} device {name} created successfully",
                "output": result.stdout,
                "router_type": router_type
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "message": f"Failed to create device: {e.stderr}",
                "error": e.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Device creation timed out after 120 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating device: {str(e)}"
            }

    def delete_router(self, name: str) -> Dict:
        """Delete router or switch (works for all device types)"""
        try:
            # First try to get the domain to determine type
            try:
                domain = self.conn.lookupByName(name)
                router_type = self.get_router_type(domain)

                # Stop the VM if running
                if domain.isActive():
                    domain.destroy()

                # Undefine (delete) the VM
                domain.undefine()

            except libvirt.libvirtError:
                pass  # VM doesn't exist in libvirt

            # Remove disk image
            import os
            disk_path = f"/var/lib/libvirt/images/{name}.qcow2"
            if os.path.exists(disk_path):
                os.remove(disk_path)

            return {
                "success": True,
                "message": f"Device {name} deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete device: {str(e)}",
                "error": str(e)
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
        """Start a stopped router or switch"""
        try:
            domain = self.conn.lookupByName(name)
            if domain.isActive():
                return {"success": False, "message": f"Device {name} is already running"}

            domain.create()
            return {"success": True, "message": f"Device {name} started"}
        except libvirt.libvirtError as e:
            return {"success": False, "message": str(e)}

    def stop_router(self, name: str, force: bool = False) -> Dict:
        """Stop a running router or switch"""
        try:
            domain = self.conn.lookupByName(name)
            if not domain.isActive():
                return {"success": False, "message": f"Device {name} is already stopped"}

            if force:
                domain.destroy()  # Force stop
            else:
                domain.shutdown()  # Graceful shutdown

            return {"success": True, "message": f"Device {name} stopped"}
        except libvirt.libvirtError as e:
            return {"success": False, "message": str(e)}

    def restart_router(self, name: str) -> Dict:
        """Restart a router or switch"""
        try:
            domain = self.conn.lookupByName(name)
            if not domain.isActive():
                return {"success": False, "message": f"Device {name} is not running"}

            domain.reboot()
            return {"success": True, "message": f"Device {name} restarting"}
        except libvirt.libvirtError as e:
            return {"success": False, "message": str(e)}

    def get_router_details(self, name: str) -> Dict:
        """Get detailed info about a router or switch"""
        try:
            domain = self.conn.lookupByName(name)
            info = domain.info()
            router_type = self.get_router_type(domain)

            return {
                "name": name,
                "state": self._get_state_name(info[0]),
                "max_memory_mb": int(info[1] / 1024),
                "memory_mb": int(info[2] / 1024),
                "vcpus": info[3],
                "cpu_time_ns": info[4],
                "id": domain.ID() if domain.ID() != -1 else None,
                "uuid": domain.UUIDString(),
                "autostart": domain.autostart() == 1,
                "router_type": router_type
            }
        except libvirt.libvirtError as e:
            return {"error": str(e)}

    def start_all_routers(self) -> Dict:
        """Start all stopped devices"""
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
        """Stop all running devices"""
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
