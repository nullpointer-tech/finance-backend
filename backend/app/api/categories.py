from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from app.core.dependencies import get_db, get_current_context
from app.services.category_service import list_categories, get_or_create_category
from datetime import datetime

router = APIRouter()

# get all cateories
@router.get("/")
async def get_categories(
    skip: int = 0,
    ctx =  Depends(get_current_context),
    db = Depends(get_db),
):
    return await list_categories(
        db=db,
        org_id=ctx["org_id"],
        skip=skip,
    )

#get category by id
@router.get("/id/{category_id}")
async def get_category_by_id(
    category_id: str,
    ctx = Depends(get_current_context),
    db = Depends(get_db),
):
    try:
        category_oid = ObjectId(category_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category ID"
        )

    category = await db.categories.find_one({
        "_id": category_oid,
        "org_id": ctx["org_id"],
        "is_deleted": {"$ne": True},
    })

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return {"message": "Category found"}

# get category by name
@router.get("/name/{category_name}")
async def get_category_by_name(
    category_name: str,
    ctx = Depends(get_current_context),
    db = Depends(get_db),
):
    category = await db.categories.find_one({
        "name": category_name,
        "org_id": ctx["org_id"],
    })

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return True

#create category
@router.post("/")
async def create_category(
    name: str,
    ctx = Depends(get_current_context),
    db = Depends(get_db),
):
    # Prevent duplicates inside the same organization
    existing = await db.categories.find_one({
        "name": name.strip(),
        "org_id": ctx["org_id"]
    })

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    await db.categories.insert_one({
        "name": name,
        "org_id": ctx["org_id"],
        "created_at": datetime.utcnow(),
        "is_deleted": False,
        "deleted_at": None,
        "updated_at": None
    })

    return {"message": "Category created"}

#update category by id
@router.put("/id/{category_id}")
async def update_category(
    category_id: str,
    name: str,
    ctx = Depends(get_current_context),
    db = Depends(get_db),
):
    result = await db.categories.update_one(
        {
            "_id": ObjectId(category_id),
            "org_id": ctx["org_id"],
        },
        {
            "$set": {
                "name": name,
                "deleted_at": datetime.utcnow(),
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": "Category updated"}

#Soft delete category
@router.delete("/id/{category_id}")
async def delete_category(
    category_id: str,
    db = Depends(get_db),
):
    try:
        oid = ObjectId(category_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid category ID")

    # Unlink from transactions
    result = await db.transactions.update_many(
        {"category_id": oid},
        {"$set": {"category_id": None}}
    )

    delete_result = await db.categories.update_one(
        {
            "_id": ObjectId(category_id)
        },
        {
            "$set": {
                "is_deleted": True,
                "updated_at": datetime.utcnow(),
            }
        }
    )

    if delete_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")

    return {
        "message": "Category deleted",
        "affected_transactions": result.modified_count
    }