from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from typing import Optional

class Transaction(BaseModel):
    id: ObjectId
    user_id: ObjectId
    type: str  # income / outcome
    amount: float
    currency: str = "PLN"
    product_id: Optional[ObjectId]
    category_id: Optional[ObjectId]
    date: datetime
    created_at: datetime
