from pydantic import BaseModel
from typing import Optional

class RouterCreate(BaseModel):
    name: str
    ip: str
    router_type: str = "vsrx"
    ram_gb: int = 4
    vcpus: int = 2

class RouterInfo(BaseModel):
    name: str
    state: str
    memory_mb: int
    vcpus: int
    id: Optional[int] = None
