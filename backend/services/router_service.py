import subprocess
import libvirt
from typing import List, Dict
import os

class RouterService:
    def __init__(self, conn: libvirt.virConnect):
        self.conn = conn

    def _is_vqfx_component(self, name: str) -> bool:
        """Check if this is a vQFX component VM (RE or PFE)"""
        return name.endswith('-re') or name.endswith('-pfe')

    def _get_vqfx_base_name(self, name: str) -> str:
        """Get base name from vQFX component name"""
        return name.replace('-re', '').replace('-pfe', '')

    def _get_vqfx_status(self, base_name: str) -> tuple:
        """Get combined status of vQFX RE and PFE"""
        try:
            re_domain = self.conn.lookupByName(f"{base_name}-re")
            pfe_domain = self.conn.lookupByName(f"{base_name}-pfe")
            
            re_active = re_domain.isActive()
            pfe_active = pfe_domain.isActive()
            
            # Both must be running for switch to be considered running
            if re_active and pfe_active:
                return ("running", re_domain, pfe_domain)
            elif not re_active and not pfe_active:
                return ("shutoff", re_domain, pfe_domain)
            else:
                return ("partial", re_domain, pfe_domain)
        except:
            return ("unknown", None, None)

    def get_router_type(self, domain) -> str:
        """Detect router/switch type from domain XML or name"""
        try:
            xml = domain.XMLDesc()
            name = domain.name()

            # Check for vQFX components
            if name.endswith('-re') or name.endswith('-pfe'):
                return 'juniper-switch'

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
        processed_vqfx = set()

        for domain in domains:
            name = domain.name()
            
            # Handle vQFX switches (combine RE and PFE into one entry)
            if self._is_vqfx_component(name):
                base_name = self._get_vqfx_base_name(name)
                
                # Skip if we already processed this vQFX
                if base_name in processed_vqfx:
                    continue
                
                processed_vqfx.add(base_name)
                
                # Get combined status
                state_name, re_domain, pfe_domain = self._get_vqfx_status(base_name)
                
                if re_domain and pfe_domain:
                    re_info = re_domain.info()
                    pfe_info = pfe_domain.info()
                    
                    routers.append({
                        "name": base_name,
                        "state": state_name,
                        "memory_mb": int((re_info[1] + pfe_info[1]) / 1024),  # Combined memory
                        "vcpus": re_info[3] + pfe_info[3],  # Combined vCPUs
                        "id": re_domain.ID() if re_domain.ID() != -1 else None,
                        "router_type": "juniper-switch"
                    })
            else:
                # Regular router or Cisco switch
                info = domain.info()
                router_type = self.get_router_type(domain)

                routers.append({
                    "name": name,
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
                cmd = ["mkjuniper", name, ip or ""]
            elif router_type.lower() in ["cisco", "csr1000v", "csr"]:
                # Cisco CSR1000v - use mkcsr1000v script
                cmd = ["mkcsr1000v", name]
            elif router_type.lower() in ["cisco-switch", "iosvl2", "viosl2"]:
                # Cisco IOSvL2 - use mkviosl2 script
                cmd = ["mkviosl2", name]
            elif router_type.lower() in ["juniper-switch", "vqfx"]:
                # Juniper vQFX - use mkvqfx script
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
            # Check if this is a vQFX switch (look for -re component)
            try:
                re_domain = self.conn.lookupByName(f"{name}-re")
                # This is a vQFX, use mkvqfx-delete script
                cmd = ["mkvqfx-delete", name]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": f"vQFX switch {name} deleted successfully"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to delete vQFX: {result.stderr}"
                    }
            except libvirt.libvirtError:
                # Not a vQFX, handle as regular device
                pass

            # Regular router or Cisco switch deletion
            try:
                domain = self.conn.lookupByName(name)
                
                # Stop the VM if running
                if domain.isActive():
                    domain.destroy()

                # Undefine (delete) the VM
                domain.undefine()

            except libvirt.libvirtError:
                pass  # VM doesn't exist in libvirt

            # Remove disk image
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
            # Check if this is a vQFX (has -re component)
            try:
                re_domain = self.conn.lookupByName(f"{name}-re")
                pfe_domain = self.conn.lookupByName(f"{name}-pfe")
                
                # This is a vQFX - start PFE first, then RE
                if pfe_domain.isActive() and re_domain.isActive():
                    return {"success": False, "message": f"vQFX {name} is already running"}
                
                # Start PFE first
                if not pfe_domain.isActive():
                    pfe_domain.create()
                
                # Wait a moment, then start RE
                import time
                time.sleep(2)
                
                if not re_domain.isActive():
                    re_domain.create()
                
                return {"success": True, "message": f"vQFX switch {name} started (PFE + RE)"}
                
            except libvirt.libvirtError:
                # Not a vQFX, handle as regular device
                pass
            
            # Regular device
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
            # Check if this is a vQFX (has -re component)
            try:
                re_domain = self.conn.lookupByName(f"{name}-re")
                pfe_domain = self.conn.lookupByName(f"{name}-pfe")
                
                # This is a vQFX - stop both
                if not re_domain.isActive() and not pfe_domain.isActive():
                    return {"success": False, "message": f"vQFX {name} is already stopped"}
                
                # Stop RE first, then PFE
                if re_domain.isActive():
                    if force:
                        re_domain.destroy()
                    else:
                        re_domain.shutdown()
                
                if pfe_domain.isActive():
                    if force:
                        pfe_domain.destroy()
                    else:
                        pfe_domain.shutdown()
                
                return {"success": True, "message": f"vQFX switch {name} stopped (RE + PFE)"}
                
            except libvirt.libvirtError:
                # Not a vQFX, handle as regular device
                pass
            
            # Regular device
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
            # Check if this is a vQFX
            try:
                re_domain = self.conn.lookupByName(f"{name}-re")
                pfe_domain = self.conn.lookupByName(f"{name}-pfe")
                
                # vQFX - restart both
                if not re_domain.isActive() or not pfe_domain.isActive():
                    return {"success": False, "message": f"vQFX {name} is not fully running"}
                
                re_domain.reboot()
                pfe_domain.reboot()
                
                return {"success": True, "message": f"vQFX switch {name} restarting"}
                
            except libvirt.libvirtError:
                pass
            
            # Regular device
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
            # Check if this is a vQFX
            try:
                re_domain = self.conn.lookupByName(f"{name}-re")
                pfe_domain = self.conn.lookupByName(f"{name}-pfe")
                
                # vQFX - combine info from both VMs
                re_info = re_domain.info()
                pfe_info = pfe_domain.info()
                
                state_name, _, _ = self._get_vqfx_status(name)
                
                return {
                    "name": name,
                    "state": state_name,
                    "max_memory_mb": int((re_info[1] + pfe_info[1]) / 1024),
                    "memory_mb": int((re_info[2] + pfe_info[2]) / 1024),
                    "vcpus": re_info[3] + pfe_info[3],
                    "cpu_time_ns": re_info[4] + pfe_info[4],
                    "id": re_domain.ID() if re_domain.ID() != -1 else None,
                    "uuid": re_domain.UUIDString(),
                    "autostart": re_domain.autostart() == 1,
                    "router_type": "juniper-switch",
                    "components": {
                        "re": {"name": f"{name}-re", "id": re_domain.ID()},
                        "pfe": {"name": f"{name}-pfe", "id": pfe_domain.ID()}
                    }
                }
                
            except libvirt.libvirtError:
                pass
            
            # Regular device
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
        processed_vqfx = set()

        for domain in domains:
            name = domain.name()
            
            # Handle vQFX components
            if self._is_vqfx_component(name):
                base_name = self._get_vqfx_base_name(name)
                if base_name in processed_vqfx:
                    continue
                processed_vqfx.add(base_name)
                
                # Start the vQFX as a unit
                result = self.start_router(base_name)
                if result["success"]:
                    started.append(base_name)
                else:
                    failed.append({"name": base_name, "error": result["message"]})
            else:
                # Regular device
                if not domain.isActive():
                    try:
                        domain.create()
                        started.append(name)
                    except Exception as e:
                        failed.append({"name": name, "error": str(e)})

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
        processed_vqfx = set()

        for domain in domains:
            name = domain.name()
            
            # Handle vQFX components
            if self._is_vqfx_component(name):
                base_name = self._get_vqfx_base_name(name)
                if base_name in processed_vqfx:
                    continue
                processed_vqfx.add(base_name)
                
                # Stop the vQFX as a unit
                result = self.stop_router(base_name, force)
                if result["success"]:
                    stopped.append(base_name)
                else:
                    failed.append({"name": base_name, "error": result["message"]})
            else:
                # Regular device
                if domain.isActive():
                    try:
                        if force:
                            domain.destroy()
                        else:
                            domain.shutdown()
                        stopped.append(name)
                    except Exception as e:
                        failed.append({"name": name, "error": str(e)})

        return {
            "success": True,
            "stopped": stopped,
            "failed": failed,
            "count": len(stopped)
        }
