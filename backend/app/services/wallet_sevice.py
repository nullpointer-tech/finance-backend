from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
from app.db.mongo import get_collection

async def apply_wallet_delta(
    wallet_id: str,
    org_id: str,
    delta: float,
    db
):
    wallets = db.wallets

    result = await wallets.update_one(
        {
            "_id": wallet_id,
            "org_id": org_id,
            "is_deleted": {"$ne": True},
        },
        {
            "$inc": {"amount": delta},
            "$set": {"updated_at": datetime.utcnow()},
        }
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Wallet not found")