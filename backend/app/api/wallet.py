from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.core.dependencies import get_db, get_current_context

router = APIRouter(tags=["Wallet-"])

@router.get("/")
async def get_wallet(
    ctx = Depends(get_current_context),
    db = Depends(get_db)
):
    wallet = await db.wallets.find_one({
        "_id": ctx["wallet_id"],
        "org_id": ctx["org_id"]
        })

    if wallet is None:
        raise HTTPException(
            status_code=404,
            detail="Wallet not found"
        )

    wallet["_id"] = str(wallet["_id"])
    wallet["org_id"] = str(wallet["org_id"])

    return wallet