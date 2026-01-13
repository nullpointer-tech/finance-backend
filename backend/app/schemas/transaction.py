from pydantic import BaseModel
from typing import Optional, Literal


class TransactionCreate(BaseModel):
    amount: float
    quantity: int = 1
    category_name: str
    product_name: str
    type: Literal["income", "outcome"]
    note: Optional[str] = None
