from pydantic import BaseModel, ConfigDict
from typing import Optional

class ElectoralRollBase(BaseModel):
    name: str
    active: bool = True

class ElectoralRollCreate(ElectoralRollBase):
    pass

class ElectoralRollRead(ElectoralRollBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
