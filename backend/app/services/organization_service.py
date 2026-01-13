from datetime import datetime
from bson import ObjectId
from app.db.mongo import get_collection

async def create_organization(name: str) -> ObjectId:
    organizations = get_collection("organizations")

    existing = await organizations.find_one({"name": name})
    if existing:
        return existing["_id"]

    result = await organizations.insert_one({
        "name": name,
        "created_at": datetime.utcnow(),
    })

    return result.inserted_id

async def create_wallet(organization_id: str) -> ObjectId:
    wallets = get_collection("wallets")

    existing = await wallets.find_one({"org_id": organization_id})
    if existing:
        return existing["_id"]

    result = await wallets.insert_one({
        "org_id": organization_id,
        "created_at": datetime.utcnow(),
        "amount": 0,
        "updated_at": None,
        "is_deleted": False
    })

    return result.inserted_id