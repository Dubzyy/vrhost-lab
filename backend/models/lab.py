from pydantic import BaseModel
from typing import List, Optional

class LabCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class LabInfo(BaseModel):
    name: str
    description: str
    router_count: int
    running_count: int
    created_at: str
