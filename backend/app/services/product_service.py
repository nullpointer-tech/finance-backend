from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
from app.db.mongo import get_collection

async def get_or_create_product(
    name: str,
    category_id: ObjectId,
    org_id: ObjectId
) -> ObjectId:
    products = get_collection("products")

    product = await products.find_one({
        "name": name,
        "org_id": org_id
    })

    if product:
        return product["_id"]

    result = await products.insert_one({
        "name": name,
        "org_id": org_id,
        "created_at": datetime.utcnow(),
        "is_deleted": False,
        "deleted_at": None,
        "updated_at": None,
        "category_id": category_id,
    })

    return result.inserted_id


async def list_products(
    db,
    org_id: str,
    skip: int,
    limit: int = 10,
):
    cursor = (
        db.products
        .find({
            "org_id": org_id,
            "is_deleted": {"$ne": True}
        })
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    products = await cursor.to_list(length=limit)
    result = []
    for doc in products:
        doc["_id"] = str(doc["_id"])
        doc["org_id"] = str(doc["org_id"])
        doc["category_id"] = str(doc["category_id"])         
        result.append(doc)

    return result

async def get_product_by_id(
    db,
    product_id: str,          
    org_id: str,
):
    product = await db.products.find_one({
        "_id": product_id,
        "org_id": org_id,
    })

    if product is None or product.get("is_deleted", False) is True:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product["_id"] = str(product["_id"])
    product["org_id"] = str(product["org_id"])
    product["category_id"] = str(product["category_id"])  

    return product