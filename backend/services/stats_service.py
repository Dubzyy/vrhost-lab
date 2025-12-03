import libvirt
import os
from typing import Dict

class StatsService:
    def __init__(self, conn: libvirt.virConnect):
        self.conn = conn
    
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        node_info = self.conn.getInfo()
        domains = self.conn.listAllDomains()
        
        running_domains = [d for d in domains if d.isActive()]
        stopped_domains = [d for d in domains if not d.isActive()]
        
        # Calculate total memory used by running VMs
        total_vm_memory = sum([d.info()[2] for d in running_domains])
        
        # Get disk usage
        disk_usage = self._get_disk_usage()
        
        return {
            "host": {
                "model": node_info[0],
                "total_memory_mb": node_info[1],
                "total_cpus": node_info[2],
                "cpu_mhz": node_info[3],
                "numa_nodes": node_info[4]
            },
            "vms": {
                "total": len(domains),
                "running": len(running_domains),
                "stopped": len(stopped_domains)
            },
            "resources": {
                "memory_used_mb": int(total_vm_memory / 1024),
                "memory_total_mb": node_info[1],
                "memory_available_mb": node_info[1] - int(total_vm_memory / 1024)
            },
            "disk": disk_usage
        }
    
    def get_router_stats(self, name: str) -> Dict:
        """Get real-time stats for a specific router"""
        try:
            domain = self.conn.lookupByName(name)
            
            if not domain.isActive():
                return {"error": "Router is not running"}
            
            info = domain.info()
            
            # Get CPU stats
            cpu_stats = domain.getCPUStats(True)[0]
            
            return {
                "name": name,
                "state": "running",
                "memory_mb": int(info[2] / 1024),
                "vcpus": info[3],
                "cpu_time_ns": info[4],
                "cpu_time_seconds": info[4] / 1000000000,
                "uptime_estimate": "calculating..."
            }
        except libvirt.libvirtError as e:
            return {"error": str(e)}
    
    def _get_disk_usage(self) -> Dict:
        """Get disk usage for libvirt images directory"""
        path = "/var/lib/libvirt/images"
        
        if not os.path.exists(path):
            return {"error": "Path not found"}
        
        stat = os.statvfs(path)
        
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
        available_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        used_gb = total_gb - available_gb
        
        return {
            "path": path,
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "available_gb": round(available_gb, 2),
            "used_percent": round((used_gb / total_gb) * 100, 2)
        }
