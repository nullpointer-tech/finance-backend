from pydantic import BaseModel
from datetime import date
from typing import Optional, Literal


class TransactionCreate(BaseModel):
    amount: float
    quantity: int = 1
    category_name: str
    product_name: str
    purchase_date: Optional[date] = None  
    type: Literal["income", "expense"]
    note: Optional[str] = None
