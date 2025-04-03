# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional
from app.models.user import user_manager
from app.utils.auth import get_current_user, get_required_user
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = None

class UserInfo(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    is_admin: bool = False
    roles: list = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录获取访问令牌"""
    user = user_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 更新最后登录时间
    user_manager.update_last_login(form_data.username)
    
    # 创建访问令牌
    access_token = user_manager.create_access_token(
        username=form_data.username,
        expires_delta=timedelta(days=1)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserInfo)
async def register(user_data: UserCreate):
    """注册新用户"""
    # 创建用户
    user = user_manager.create_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        display_name=user_data.display_name
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
        
    return user

@router.get("/me", response_model=UserInfo)
async def read_users_me(current_user: Dict = Depends(get_required_user)):
    """获取当前登录用户信息"""
    return current_user

@router.put("/me", response_model=UserInfo)
async def update_user_me(user_data: UserUpdate, current_user: Dict = Depends(get_required_user)):
    """更新当前用户信息"""
    updated_user = user_manager.update_user(
        username=current_user["username"],
        data=user_data.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新用户信息失败"
        )
        
    return updated_user 