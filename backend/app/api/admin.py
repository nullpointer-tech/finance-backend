from fastapi import APIRouter, HTTPException
from app.db.mongo import get_collection
from app.core.security import hash_password
from app.services.organization_service import create_organization, create_wallet

router = APIRouter()

@router.post("/register")
async def register_admin(
    username: str,
    password: str,
    organization: str
):
    users = get_collection("users")

    existing = await users.find_one({"username": username})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    organization_id = await create_organization(organization)
    wallet_id = await create_wallet(organization_id)
    user = {
        "username": username,
        "password_hash": hash_password(password),
        "is_admin": True,
        "organization": organization_id,
        "wallet_id": wallet_id
    }

    await users.insert_one(user)

    return {"message": "User created"}