from pydantic import BaseModel
from typing import Optional

class Link(BaseModel):
    """Network link between two routers"""
    id: str  # Generated ID like "vSRX1-ge000-vQFX1-ge001"
    source_router: str  # Source router name
    source_interface: str  # Source interface name
    target_router: str  # Target router name
    target_interface: str  # Target interface name
    status: str = "down"  # up, down
    lab: Optional[str] = None  # Lab this link belongs to

class LinkCreate(BaseModel):
    """Request to create a new link"""
    source_router: str
    source_interface: str
    target_router: str
    target_interface: str
    lab: Optional[str] = None
