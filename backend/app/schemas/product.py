from pydantic import BaseModel
from typing import Optional

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[str] = None