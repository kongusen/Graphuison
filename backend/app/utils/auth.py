from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict

from backend.app.models.user import user_manager

# OAuth2密码流认证
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    auto_error=False  # 不自动抛出401错误
)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[Dict]:
    """获取当前用户
    
    Args:
        token: JWT令牌
        
    Returns:
        用户信息
    """
    if not token:
        return None
        
    user = user_manager.verify_token(token)
    return user

async def get_required_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """获取当前用户（必须已登录）
    
    Args:
        token: JWT令牌
        
    Returns:
        用户信息
        
    Raises:
        HTTPException: 未登录或令牌无效
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = user_manager.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

async def get_admin_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """获取当前管理员用户
    
    Args:
        token: JWT令牌
        
    Returns:
        用户信息
        
    Raises:
        HTTPException: 未登录、令牌无效或不是管理员
    """
    user = await get_required_user(token)
    
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
        
    return user 