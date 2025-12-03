import json
import os
from typing import List, Dict
from datetime import datetime

class TopologyService:
    def __init__(self, storage_path: str = "/opt/vrhost-lab/topologies"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def save_topology(self, name: str, description: str, routers: List[Dict]) -> Dict:
        """Save current lab topology"""
        topology = {
            "name": name,
            "description": description,
            "routers": routers,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        file_path = os.path.join(self.storage_path, f"{name}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(topology, f, indent=2)
            
            return {
                "success": True,
                "message": f"Topology '{name}' saved successfully",
                "path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to save topology: {str(e)}"
            }
    
    def load_topology(self, name: str) -> Dict:
        """Load a saved topology"""
        file_path = os.path.join(self.storage_path, f"{name}.json")
        
        if not os.path.exists(file_path):
            return {"error": f"Topology '{name}' not found"}
        
        try:
            with open(file_path, 'r') as f:
                topology = json.load(f)
            return topology
        except Exception as e:
            return {"error": f"Failed to load topology: {str(e)}"}
    
    def list_topologies(self) -> List[Dict]:
        """List all saved topologies"""
        topologies = []
        
        if not os.path.exists(self.storage_path):
            return topologies
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        topo = json.load(f)
                    topologies.append({
                        "name": topo.get("name"),
                        "description": topo.get("description", ""),
                        "router_count": len(topo.get("routers", [])),
                        "created_at": topo.get("created_at")
                    })
                except:
                    continue
        
        return topologies
    
    def delete_topology(self, name: str) -> Dict:
        """Delete a saved topology"""
        file_path = os.path.join(self.storage_path, f"{name}.json")
        
        if not os.path.exists(file_path):
            return {"success": False, "message": f"Topology '{name}' not found"}
        
        try:
            os.remove(file_path)
            return {
                "success": True,
                "message": f"Topology '{name}' deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete topology: {str(e)}"
            }
