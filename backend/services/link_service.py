from typing import List, Dict, Optional
from backend.models.link import Link, LinkCreate
import json
import os

class LinkService:
    """Service for managing network links between routers"""

    def __init__(self, data_dir: str = "/opt/vrhost-lab/data"):
        self.data_dir = data_dir
        self.links_file = os.path.join(data_dir, "links.json")
        self.links: Dict[str, Link] = {}
        self._load_links()

    def _load_links(self):
        """Load links from JSON file"""
        try:
            if os.path.exists(self.links_file):
                with open(self.links_file, 'r') as f:
                    data = json.load(f)
                    self.links = {k: Link(**v) for k, v in data.items()}
                print(f"✓ Loaded {len(self.links)} links from {self.links_file}")
        except Exception as e:
            print(f"⚠ Could not load links: {e}")
            self.links = {}

    def _save_links(self):
        """Save links to JSON file"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.links_file, 'w') as f:
                data = {k: v.dict() for k, v in self.links.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save links: {e}")

    def _generate_link_id(self, source_router: str, source_interface: str,
                          target_router: str, target_interface: str) -> str:
        """Generate unique link ID"""
        # Clean interface names (remove slashes, colons)
        src_if = source_interface.replace('/', '').replace(':', '').replace('-', '')
        tgt_if = target_interface.replace('/', '').replace(':', '').replace('-', '')
        return f"{source_router}-{src_if}-{target_router}-{tgt_if}"

    def create_link(self, link_create: LinkCreate, router_service=None) -> Dict:
        """Create a new network link"""
        try:
            link_id = self._generate_link_id(
                link_create.source_router,
                link_create.source_interface,
                link_create.target_router,
                link_create.target_interface
            )

            # Check if link already exists
            if link_id in self.links:
                return {
                    "success": False,
                    "message": f"Link already exists: {link_id}"
                }

            # Determine initial status based on router states
            initial_status = "down"
            if router_service:
                try:
                    source_details = router_service.get_router_details(link_create.source_router)
                    target_details = router_service.get_router_details(link_create.target_router)
                    
                    source_state = source_details.get('state', 'unknown')
                    target_state = target_details.get('state', 'unknown')
                    
                    # Link is up only if BOTH routers are running
                    if source_state == 'running' and target_state == 'running':
                        initial_status = "up"
                        print(f"✓ Link created with status 'up' (both routers running)")
                    else:
                        print(f"⚠ Link created with status 'down' (source: {source_state}, target: {target_state})")
                except Exception as e:
                    print(f"⚠ Could not check router states: {e}")

            # Create the link
            link = Link(
                id=link_id,
                source_router=link_create.source_router,
                source_interface=link_create.source_interface,
                target_router=link_create.target_router,
                target_interface=link_create.target_interface,
                status=initial_status,
                lab=link_create.lab
            )

            self.links[link_id] = link
            self._save_links()

            return {
                "success": True,
                "message": f"Link created: {link_id}",
                "link": link.dict()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create link: {str(e)}"
            }

    def delete_link(self, link_id: str) -> Dict:
        """Delete a network link"""
        if link_id not in self.links:
            return {
                "success": False,
                "message": f"Link not found: {link_id}"
            }

        del self.links[link_id]
        self._save_links()

        return {
            "success": True,
            "message": f"Link deleted: {link_id}"
        }

    def get_link(self, link_id: str) -> Optional[Link]:
        """Get a specific link"""
        return self.links.get(link_id)

    def list_links(self, lab: Optional[str] = None) -> List[Dict]:
        """List all links, optionally filtered by lab"""
        links_list = list(self.links.values())

        if lab:
            links_list = [link for link in links_list if link.lab == lab]

        return [link.dict() for link in links_list]

    def get_router_links(self, router_name: str) -> List[Dict]:
        """Get all links connected to a specific router"""
        router_links = []

        for link in self.links.values():
            if link.source_router == router_name or link.target_router == router_name:
                router_links.append(link.dict())

        return router_links

    def update_link_status(self, link_id: str, status: str) -> Dict:
        """Update link status (up/down)"""
        if link_id not in self.links:
            return {
                "success": False,
                "message": f"Link not found: {link_id}"
            }

        self.links[link_id].status = status
        self._save_links()

        return {
            "success": True,
            "message": f"Link status updated: {link_id} -> {status}"
        }

    def update_links_for_router(self, router_name: str, router_state: str, router_service=None):
        """Update all links for a router based on its state - checks BOTH routers"""
        updated_count = 0
        
        for link in self.links.values():
            if link.source_router == router_name or link.target_router == router_name:
                # Determine the other router in this link
                other_router = link.target_router if link.source_router == router_name else link.source_router
                
                # Check if BOTH routers are running
                if router_service:
                    try:
                        other_details = router_service.get_router_details(other_router)
                        other_state = other_details.get('state', 'unknown')
                        
                        # Link is up only if BOTH routers are running
                        old_status = link.status
                        if router_state == 'running' and other_state == 'running':
                            link.status = 'up'
                        else:
                            link.status = 'down'
                        
                        if old_status != link.status:
                            print(f"✓ Link {link.id}: {old_status} -> {link.status} ({router_name}: {router_state}, {other_router}: {other_state})")
                            updated_count += 1
                    except Exception as e:
                        print(f"⚠ Could not check state of {other_router}: {e}")
                        link.status = 'down'
                        updated_count += 1
                else:
                    # Fallback: simple logic if router_service not available
                    old_status = link.status
                    link.status = 'up' if router_state == 'running' else 'down'
                    if old_status != link.status:
                        updated_count += 1

        if updated_count > 0:
            self._save_links()
            print(f"✓ Updated {updated_count} link(s) for router {router_name}")

    def delete_router_links(self, router_name: str) -> int:
        """Delete all links connected to a router (when router is deleted)"""
        links_to_delete = [
            link_id for link_id, link in self.links.items()
            if link.source_router == router_name or link.target_router == router_name
        ]

        for link_id in links_to_delete:
            del self.links[link_id]

        if links_to_delete:
            self._save_links()

        return len(links_to_delete)
