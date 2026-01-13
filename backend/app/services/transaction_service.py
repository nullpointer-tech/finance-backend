from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId

async def list_transactions(
    db,
    org_id: str,
    start_date: datetime,
    end_date: datetime,
    skip: int,
    limit: int = 10,
):
    cursor = (
        db.transactions
        .find({
            "org_id": org_id,
            "created_at": {"$gte": start_date, "$lte": end_date},
            "is_deleted": {"$ne": True}
        })
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    transactions = await cursor.to_list(length=limit)
    result = []
    for doc in transactions:
        doc["_id"] = str(doc["_id"])
        doc["org_id"] = str(doc["org_id"])
        doc["user_id"] = str(doc["user_id"])
        doc["category_id"] = str(doc["category_id"])
        doc["product_id"] = str(doc["product_id"])               
        result.append(doc)

    return result

async def get_transaction_by_id(
    db,
    transaction_id: str,          
    org_id: str = None
):
    try:
        object_id = ObjectId(transaction_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid transaction ID format"
        )

    filter_query = {"_id": object_id}

    if org_id:
        filter_query["org_id"] = org_id

    transaction = await db.transactions.find_one(filter_query)

    if transaction is None or transaction.get("is_deleted", False) is True:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    transaction["_id"] = str(transaction["_id"])
    transaction["org_id"] = str(transaction["org_id"])
    transaction["category_id"] = str(transaction["category_id"])  
    transaction["user_id"] = str(transaction["user_id"])
    transaction["product_id"] = str(transaction["product_id"])

    return transaction
