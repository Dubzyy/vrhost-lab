from pydantic import BaseModel
from typing import Optional, List

class RouterInterface(BaseModel):
    """Network interface on a router"""
    name: str  # e.g., "ge-0/0/0", "GigabitEthernet0/0"
    mac_address: Optional[str] = None
    connected_to: Optional[str] = None  # Router name this interface connects to
    connected_interface: Optional[str] = None  # Interface name on the other router
    status: str = "down"  # up, down, admin-down

class RouterCreate(BaseModel):
    name: str
    ip: str
    router_type: str = "vsrx"
    ram_gb: int = 4
    vcpus: int = 2
    lab: Optional[str] = None  # Lab assignment

class RouterInfo(BaseModel):
    name: str
    state: str
    memory_mb: int
    vcpus: int
    id: Optional[int] = None
    router_type: Optional[str] = "vsrx"
    lab: Optional[str] = None
    interfaces: List[RouterInterface] = []
    ip: Optional[str] = None
