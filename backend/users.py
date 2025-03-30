from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Union
from auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

class User(BaseModel):
    id: int
    name: str
    email: str

# Simuleer een database met een lijst van gebruikers
fake_users_db = [
    {"id": 1, "name": "Admin", "email": "admin@example.com"},
    {"id": 2, "name": "Alice", "email": "alice@example.com"},
    {"id": 3, "name": "Bob", "email": "bob@example.com"}
]
next_id = 3

@router.get("/", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Haal alle gebruikers op. Alleen toegankelijk voor geauthenticeerde gebruikers."""
    return fake_users_db


@router.get("/users/{user_id}", response_model=User)
async def get_user_by_id(user_id: int, current_user: dict = Depends(get_current_user)):
    for user in fake_users_db.values():
        if user.get("id") == user_id:
            return User(
                id=user["id"],
                username=user["username"],
                role=user["role"],
                email=user.get("email")
            )
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/", response_model=User, status_code=201)
async def create_user(user: User, current_user: dict = Depends(get_current_user)):
    global next_id
    user_dict = user.dict()
    user_dict["id"] = next_id
    next_id += 1
    fake_users_db.append(user_dict)
    return user_dict

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: User, current_user: dict = Depends(get_current_user)):
    for index, existing_user in enumerate(fake_users_db):
        if existing_user["id"] == user_id:
            updated_user = user.dict()
            updated_user["id"] = user_id
            fake_users_db[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}", response_model=User)
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    for index, user in enumerate(fake_users_db):
        if user["id"] == user_id:
            removed_user = fake_users_db.pop(index)
            return removed_user
    raise HTTPException(status_code=404, detail="User not found")
