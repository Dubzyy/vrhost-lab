import json
import os
from typing import List, Dict
from datetime import datetime

class LabService:
    def __init__(self, storage_path: str = "/opt/vrhost-lab/labs"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def create_lab(self, name: str, description: str = "") -> Dict:
        """Create a new lab"""
        lab = {
            "name": name,
            "description": description,
            "routers": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        file_path = os.path.join(self.storage_path, f"{name}.json")
        
        if os.path.exists(file_path):
            return {"success": False, "message": f"Lab '{name}' already exists"}
        
        try:
            with open(file_path, 'w') as f:
                json.dump(lab, f, indent=2)
            return {"success": True, "message": f"Lab '{name}' created", "lab": lab}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def list_labs(self, router_service) -> List[Dict]:
        """List all labs with router counts"""
        labs = []
        
        if not os.path.exists(self.storage_path):
            return labs
        
        all_routers = router_service.list_routers()
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        lab = json.load(f)
                    
                    # Count routers in this lab
                    lab_prefix = lab['name'] + "-"
                    lab_routers = [r for r in all_routers if r['name'].startswith(lab_prefix)]
                    running_routers = [r for r in lab_routers if r['state'] == 'running']
                    
                    labs.append({
                        "name": lab['name'],
                        "description": lab.get('description', ''),
                        "router_count": len(lab_routers),
                        "running_count": len(running_routers),
                        "created_at": lab.get('created_at', '')
                    })
                except:
                    continue
        
        return labs
    
    def get_lab(self, name: str) -> Dict:
        """Get lab details"""
        file_path = os.path.join(self.storage_path, f"{name}.json")
        
        if not os.path.exists(file_path):
            return {"error": f"Lab '{name}' not found"}
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    
    def delete_lab(self, name: str) -> Dict:
        """Delete a lab (doesn't delete routers)"""
        file_path = os.path.join(self.storage_path, f"{name}.json")
        
        if not os.path.exists(file_path):
            return {"success": False, "message": f"Lab '{name}' not found"}
        
        try:
            os.remove(file_path)
            return {"success": True, "message": f"Lab '{name}' deleted"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_lab_routers(self, lab_name: str, router_service) -> List[Dict]:
        """Get all routers belonging to a lab"""
        all_routers = router_service.list_routers()
        lab_prefix = lab_name + "-"
        return [r for r in all_routers if r['name'].startswith(lab_prefix)]
