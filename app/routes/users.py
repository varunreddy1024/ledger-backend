from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from app.security import get_current_active_admin, User
from app.models.auth import UserCreate, UserRole
from app.security import get_password_hash, db

router = APIRouter()

@router.get("", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_active_admin)):
    """
    Get all users. Only accessible by admin users.
    """
    users = await db["users"].find().to_list(length=None)
    return [
        User(
            id=str(user["_id"]),
            email=user["email"],
            username=user["username"],
            full_name=user.get("full_name"),
            role=user["role"]
        ) for user in users
    ]

@router.post("", response_model=User)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_active_admin)
):
    """
    Create a new user. Only accessible by admin users.
    """
    # Check if username already exists
    if await db["users"].find_one({"username": user_create.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if await db["users"].find_one({"email": user_create.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user_dict = user_create.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    
    result = await db["users"].insert_one(user_dict)
    
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    return User(
        id=str(created_user["_id"]),
        email=created_user["email"],
        username=created_user["username"],
        full_name=created_user.get("full_name"),
        role=created_user["role"]
    )

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserCreate,
    current_user: User = Depends(get_current_active_admin)
):
    """
    Update a user. Only accessible by admin users.
    """
    # Check if user exists
    existing_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check username uniqueness (excluding current user)
    username_exists = await db["users"].find_one({
        "_id": {"$ne": ObjectId(user_id)},
        "username": user_update.username
    })
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Check email uniqueness (excluding current user)
    email_exists = await db["users"].find_one({
        "_id": {"$ne": ObjectId(user_id)},
        "email": user_update.email
    })
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    return User(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        username=updated_user["username"],
        full_name=updated_user.get("full_name"),
        role=updated_user["role"]
    )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_admin)
):
    """
    Delete a user. Only accessible by admin users.
    """
    result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"detail": "User deleted successfully"}