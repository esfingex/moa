from pydantic import BaseModel, ConfigDict
from typing import Optional

class PapernewsBase(BaseModel):
    name: str
    active: bool = True

class PapernewsCreate(PapernewsBase):
    pass

class PapernewsRead(PapernewsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
