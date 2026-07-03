from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

# Used for creating an item
class ItemCreate(ItemBase):
    pass

# Used for returning an item to the user
class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True