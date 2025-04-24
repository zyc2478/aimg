from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core import security
from ..schemas import user as user_schemas
from ..crud import user as user_crud
from ..database import get_db

router = APIRouter()

@router.post("/register", response_model=user_schemas.User)
async def register_user(
    user: user_schemas.UserCreate,
    db: Session = Depends(get_db)
):
    db_user = user_crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    return user_crud.create_user(db, user)

@router.get("/me", response_model=user_schemas.User)
async def read_users_me(
    current_user = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    return current_user 