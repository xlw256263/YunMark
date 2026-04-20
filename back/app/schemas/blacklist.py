from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlacklistBase(BaseModel):
    pattern: str
    description: Optional[str] = None

class BlacklistCreate(BlacklistBase):
    pass

class BlacklistResponse(BlacklistBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
