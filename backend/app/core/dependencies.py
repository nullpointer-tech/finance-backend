from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from bson import ObjectId

from app.db.mongo import mongo
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    if mongo.db is None:
        raise HTTPException(
            status_code=500,
            detail="Database not initialized"
        )
    return mongo.db


async def get_current_context(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id = ObjectId(payload["sub"])
        org_id = ObjectId(payload["org"])
        is_admin = payload.get("is_admin", False)
        wallet_id = ObjectId(payload["wallet_id"])

        return {
            "user_id": user_id,
            "org_id": org_id,
            "is_admin": is_admin,
            "wallet_id": wallet_id
        }

    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(context: dict = Depends(get_current_context)):
    return context["user_id"]


async def get_current_org(context: dict = Depends(get_current_context)):
    return context["org_id"]


async def get_admin_user(
    context: dict = Depends(get_current_context),
    db = Depends(get_db),
):
    if not context["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )

    user = await db.users.find_one({"_id": context["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
