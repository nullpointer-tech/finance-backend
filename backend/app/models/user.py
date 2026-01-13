from pydantic import BaseModel, Field
from bson import ObjectId

class User(BaseModel):
    id: ObjectId = Field(alias="_id")
    username: str
    password_hash: str
    is_admin: bool = False
