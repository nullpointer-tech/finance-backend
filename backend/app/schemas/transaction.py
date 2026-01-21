from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, Literal


class TransactionCreate(BaseModel):
    amount: float
    quantity: int = 1
    category_name: str
    product_name: str
    purchase_date: date  
    type: Literal["income", "expense"]
    note: Optional[str] = None

    @field_validator('purchase_date', mode='before')
    @classmethod
    def convert_date_to_datetime(cls, v):
        if isinstance(v, date) and not isinstance(v, datetime):
            return datetime.combine(v, datetime.min.time())
        return v
