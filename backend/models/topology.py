from pydantic import BaseModel
from typing import List, Optional

class TopologyRouter(BaseModel):
    name: str
    ip: str
    router_type: str
    ram_gb: int
    vcpus: int

class Topology(BaseModel):
    name: str
    description: Optional[str] = ""
    routers: List[TopologyRouter]

class TopologyInfo(BaseModel):
    name: str
    description: str
    router_count: int
    created_at: Optional[str] = None
