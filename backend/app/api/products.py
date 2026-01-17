from fastapi import APIRouter, HTTPException, Depends, status, Body
from bson import ObjectId
from app.core.dependencies import get_db, get_current_context
from datetime import datetime
from app.services.product_service import list_products, get_product_by_id
from app.schemas.product import ProductUpdate


router = APIRouter()

#Create new product 
@router.post("/")
async def create_product(
    name: str,
    category_id: str,
    ctx: dict =  Depends(get_current_context),
    db = Depends(get_db),
):
    existing = await db.products.find_one({
        "name": name,
        "org_id": ctx.get("org_id"),
        "is_deleted": {"$ne": True},
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already exists"
        )
    try:
        category_object_id = ObjectId(category_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid category ID format"
        )
    await db.products.insert_one({
        "name": name,
        "org_id": ctx["org_id"],
        "created_at": datetime.utcnow(),
        "is_deleted": False,
        "deleted_at": None,
        "updated_at": None,
        "category_id": category_object_id,
    })

    return {"message": "Product is created"}

# get all products
@router.get("/")
async def get_products(
    ctx = Depends(get_current_context),
    db = Depends(get_db),
    skip: int = 0, 
):
    return await list_products(
        db=db,
        org_id=ctx["org_id"],
        skip=skip,
    )

#get product by ID
@router.get("/id/{product_id}")
async def get_product_by_id(
    product_id: str,
    ctx = Depends(get_current_context),
    db = Depends(get_db)
):
    org_id = ctx("org_id")
    
    product = await get_product_by_id(
        db=db,
        product_id=product_id,
        org_id=org_id
    )
    
    return product

@router.put("/id/{product_id}")
async def update_product(
    product_id: str,
    update_data: ProductUpdate = Body(...),
    ctx: dict =  Depends(get_current_context),
    db = Depends(get_db),
):
    org_id = ctx.get("org_id")
    if not org_id:
        raise HTTPException(403, "Organization context required")

    try:
        object_id = ObjectId(product_id)
    except Exception:
        raise HTTPException(400, "Invalid product ID")

    # Build update dictionary — only include fields that were provided
    update_fields = {}
    
    if update_data.name is not None:
        update_fields["name"] = update_data.name.strip()
    
    if update_data.category_id is not None:
        try:
            update_fields["category_id"] = ObjectId(update_data.category_id)
        except Exception:
            raise HTTPException(400, "Invalid category ID format")

    if not update_fields:
        raise HTTPException(400, "No fields provided to update")

    update_fields["updated_at"] = datetime.utcnow()

    result = await db.products.update_one(
        {
            "_id": object_id,
            "org_id": org_id,    
        },
        {"$set": update_fields}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Product not found or no changes applied"
        )

    return {"message": "Product updated successfully"}

@router.delete("/{product_id}")
async def product_delete_soft(
    product_id: str,
    ctx: dict =  Depends(get_current_context),
    db = Depends(get_db),
):      
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    # Unlink from transactions
    result = await db.transactions.update_many(
        {"product_id": oid},
        {"$set": {"product_id": None}}
    )

    delete_result = await db.products.update_one(
        {
            "_id": ObjectId(product_id)
        },
        {
            "$set": {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
            }
        }
    )

    if delete_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "message": "Product deleted",
        "affected_transactions": result.modified_count
    }