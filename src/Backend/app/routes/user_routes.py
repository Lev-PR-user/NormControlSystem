from fastapi import APIRouter, Depends, HTTPException, status, Body
from app.services.users.users import (
    create_user,
    authenticate_user,
    get_user_profile,
)
from app.core.security import get_current_user
from typing import Dict, Any

router = APIRouter(tags=["users"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: Dict[str, Any] = Body(...)):
    return create_user(user_data)

@router.post("/login")
async def login(
    email: str = Body(..., embed=True),
    password: str = Body(..., embed=True)
):
    return authenticate_user(email, password)

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Не удалось получить ID пользователя из токена"
        )
    
    return get_user_profile(user_id)