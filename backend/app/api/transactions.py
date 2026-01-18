from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.core.dependencies import get_db, get_current_context
from app.schemas.transaction import TransactionCreate
from app.services.transaction_service import list_transactions, get_transaction_by_id
from app.services.category_service import get_or_create_category
from app.services.product_service import get_or_create_product
from bson import ObjectId
from app.services.wallet_sevice import apply_wallet_delta


router = APIRouter(tags=["Transactions"])

@router.post("/")
async def create_transaction(
    payload: TransactionCreate,
    ctx: dict = Depends(get_current_context),
    db = Depends(get_db),
):
    category_id = await get_or_create_category(
        name=payload.category_name,
        organization_id=ctx.get("org_id")
    )

    product_id = None
    if payload.product_name:
        product_id = await get_or_create_product(
            name=payload.product_name,
            category_id=category_id,
            org_id=ctx["org_id"],
        )

    transaction = {
        "org_id": ctx["org_id"],
        "user_id": ctx["user_id"],
        "type": payload.type,
        "amount": payload.amount,
        "category_id": category_id,
        "product_id": product_id,
        "note": payload.note,
        "quantity": payload.quantity,
        "created_at": datetime.utcnow(),
        "is_deleted": False,
        "deleted_at": None,
    }
    if payload.type == "income":
        delta = payload.amount
    elif payload.type == "expense":
        delta = -payload.amount
    else:
        raise HTTPException(400, "Invalid transaction type")
    
    await apply_wallet_delta(
        db=db,
        wallet_id=ctx["wallet_id"],
        org_id=ctx["org_id"],
        delta=delta,
    )

    await db.transactions.insert_one(transaction)

    return {"message": "Transaction created"}

@router.delete("/id/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    ctx = Depends(get_current_context),
    db = Depends(get_db),
):
    tx = await db.transactions.find_one({"_id": ObjectId(transaction_id),})
    if tx["type"] == "income":
        delta = -tx["amount"]
    else: 
        delta = tx["amount"]

    await apply_wallet_delta(
        db=db,
        wallet_id=ctx["wallet_id"],
        org_id=ctx["org_id"],
        delta=delta,
    )   

    result = await db.transactions.update_one(
        {
            "_id": ObjectId(transaction_id),
            "org_id": ctx["org_id"],
            "is_deleted": False,
        },
        {
            "$set": {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Transaction not found")

    return {"message": "Transaction deleted"}

@router.get("/")
async def get_transactions(
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    ctx =  Depends(get_current_context),
    db = Depends(get_db),
):
    return await list_transactions(
        db=db,
        org_id=ctx["org_id"],
        start_date=start_date,
        end_date=end_date,
        skip=skip,
    )

@router.get("/id/{transaction_id}")
async def ger_transaction_by_id(
    transaction_id: str,
    ctx: dict = Depends(get_current_context),
    db = Depends(get_db)
):
    org_id = ctx.get("org_id")
    
    product = await get_transaction_by_id(
        db=db,
        transaction_id=transaction_id,
        org_id=org_id
    )
    
    return product