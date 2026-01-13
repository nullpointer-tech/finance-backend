from bson import ObjectId
from app.db.mongo import get_collection
from datetime import datetime

async def delete_category(db, category_id: ObjectId, user_id: ObjectId):
    affected = await db.transactions.update_many(
        {"user_id": user_id, "category_id": category_id},
        {"$set": {"category_id": None}}
    )

    await db.categories.delete_one({"_id": category_id})
    return affected.modified_count

async def get_or_create_category(
    name: str,
    organization_id: str
):
    categories = get_collection("categories")

    category = await categories.find_one({
        "name": name,
        "org_id": organization_id
    })
    if category:
        return category["_id"]

    result = await categories.insert_one({
        "name": name,
        "org_id": organization_id,
        "created_at": datetime.utcnow(),
        "is_deleted": False,
        "deleted_at": None,
        "updated_at": None
    })

    return result.inserted_id

async def list_categories(
    db,
    org_id: str,
    skip: int,
    limit: int = 10,
):
    cursor = (
        db.categories
        .find({
            "org_id": org_id,
            "is_deleted": {"$ne": True}
        })
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    categories = await cursor.to_list(length=limit)
    result = []
    for doc in categories:
        doc["_id"] = str(doc["_id"])
        doc["org_id"] = str(doc["org_id"])             
        result.append(doc)

    return result