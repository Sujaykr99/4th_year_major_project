"""Authentication endpoints."""
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.core.config import settings
from app.core.database import get_database
from app.models.schemas import Token, UserCreate, UserInDB, UserResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = await db.users.find_one({"$or": [{"email": user_in.email}, {"username": user_in.username}]})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists",
        )

    # Hash password and create user
    hashed_password = security.get_password_hash(user_in.password)
    user_dict = user_in.model_dump()
    del user_dict["password"]
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()

    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)

    return UserResponse(**user_dict)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Find user by email (username field in OAuth2 form)
    user_dict = await db.users.find_one({"email": form_data.username})
    if not user_dict:
        # Also try username field
        user_dict = await db.users.find_one({"username": form_data.username})

    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_in_db = UserInDB(**user_dict)
    if not security.verify_password(form_data.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user_in_db.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get current user information.
    """
    user_dict = await db.users.find_one({"_id": current_user_id})
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    user_dict["id"] = str(user_dict["_id"])
    return UserResponse(**user_dict)