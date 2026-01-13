from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.mongo import get_collection
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if get_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    users = get_collection("users")
    user = await users.find_one({"username": form.username})
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={
            "sub": str(user["_id"]), 
            "is_admin": user.get("is_admin", False), 
            "org": str(user["organization"]),
            "wallet_id": str(user["wallet_id"])
            }
    )
    return {"access_token": access_token, "token_type": "bearer"}

