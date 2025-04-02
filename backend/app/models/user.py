# backend/app/models/user.py
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging
import hashlib
import jwt
from passlib.context import CryptContext
from backend.app.config import settings

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager:
    """用户管理类"""
    
    def __init__(self, base_dir: str = None):
        """初始化用户管理
        
        Args:
            base_dir: 用户数据存储的基础目录
        """
        self.base_dir = base_dir or os.path.join(settings.BASE_DIR, "data", "users")
        self._ensure_dir_exists(self.base_dir)
        self.user_db_path = os.path.join(self.base_dir, "users.json")
        self.users = self._load_users()
        
    def _ensure_dir_exists(self, path: str) -> None:
        """确保目录存在，不存在则创建"""
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
    def _load_users(self) -> Dict:
        """加载用户数据"""
        if os.path.exists(self.user_db_path):
            try:
                with open(self.user_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载用户数据失败: {e}")
                return {}
        return {}
        
    def _save_users(self) -> None:
        """保存用户数据"""
        try:
            with open(self.user_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存用户数据失败: {e}")
            
    def get_user(self, username: str) -> Optional[Dict]:
        """获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            用户信息字典，不存在则返回None
        """
        return self.users.get(username)
        
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典，不存在则返回None
        """
        for username, user_data in self.users.items():
            if user_data.get("id") == user_id:
                return user_data
        return None
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码
            
        Returns:
            密码是否正确
        """
        return pwd_context.verify(plain_password, hashed_password)
        
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            密码哈希
        """
        return pwd_context.hash(password)
        
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """认证用户
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            认证通过返回用户信息，否则返回None
        """
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.get("hashed_password", "")):
            return None
        return user
        
    def create_user(self, username: str, password: str, email: str, display_name: str = "") -> Optional[Dict]:
        """创建用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            display_name: 显示名称，默认为空
            
        Returns:
            创建成功返回用户信息，用户名已存在则返回None
        """
        if username in self.users:
            return None
            
        # 生成唯一用户ID
        user_id = str(uuid.uuid4())
        
        # 哈希密码
        hashed_password = self.get_password_hash(password)
        
        # 创建用户记录
        now = datetime.now().isoformat()
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "display_name": display_name or username,
            "created_at": now,
            "updated_at": now,
            "last_login": None,
            "is_active": True,
            "is_admin": False,
            "roles": ["user"],
            "preferences": {}
        }
        
        # 保存用户数据
        self.users[username] = user_data
        self._save_users()
        
        # 返回用户信息（不包含密码）
        user_info = user_data.copy()
        user_info.pop("hashed_password", None)
        return user_info
        
    def update_user(self, username: str, data: Dict) -> Optional[Dict]:
        """更新用户信息
        
        Args:
            username: 用户名
            data: 要更新的数据
            
        Returns:
            更新后的用户信息，用户不存在则返回None
        """
        user = self.get_user(username)
        if not user:
            return None
            
        # 禁止更新敏感字段
        for key in ["id", "username", "hashed_password", "created_at", "is_admin", "roles"]:
            data.pop(key, None)
            
        # 如果需要更新密码
        if "password" in data:
            user["hashed_password"] = self.get_password_hash(data.pop("password"))
            
        # 更新其他字段
        user.update(data)
        user["updated_at"] = datetime.now().isoformat()
        
        # 保存更新
        self.users[username] = user
        self._save_users()
        
        # 返回用户信息（不包含密码）
        user_info = user.copy()
        user_info.pop("hashed_password", None)
        return user_info
        
    def update_last_login(self, username: str) -> None:
        """更新最后登录时间
        
        Args:
            username: 用户名
        """
        user = self.get_user(username)
        if user:
            user["last_login"] = datetime.now().isoformat()
            self.users[username] = user
            self._save_users()
            
    def delete_user(self, username: str) -> bool:
        """删除用户
        
        Args:
            username: 用户名
            
        Returns:
            是否删除成功
        """
        if username not in self.users:
            return False
            
        self.users.pop(username)
        self._save_users()
        return True
        
    def create_access_token(self, username: str, expires_delta: timedelta = None) -> str:
        """创建访问令牌
        
        Args:
            username: 用户名
            expires_delta: 过期时间增量，默认为1天
            
        Returns:
            JWT令牌
        """
        user = self.get_user(username)
        if not user:
            raise ValueError(f"用户 {username} 不存在")
            
        if expires_delta is None:
            expires_delta = timedelta(days=1)
            
        expire = datetime.utcnow() + expires_delta
        
        # 创建令牌数据
        token_data = {
            "sub": user["id"],
            "username": username,
            "roles": user.get("roles", ["user"]),
            "exp": expire
        }
        
        # 使用JWT创建令牌
        encoded_jwt = jwt.encode(
            token_data, 
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        
        return encoded_jwt
        
    def verify_token(self, token: str) -> Optional[Dict]:
        """验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            验证通过返回用户信息，否则返回None
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = payload.get("sub")
            
            user = self.get_user_by_id(user_id)
            if not user:
                return None
                
            # 返回用户信息（不包含密码）
            user_info = user.copy()
            user_info.pop("hashed_password", None)
            return user_info
            
        except jwt.PyJWTError as e:
            logger.error(f"验证令牌失败: {e}")
            return None

# 创建用户管理实例
user_manager = UserManager() 