# backend/app/utils/document_storage.py
import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, BinaryIO
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class DocumentStorage:
    """文档存储管理类"""
    
    def __init__(self, base_dir: str = None):
        """初始化文档存储
        
        Args:
            base_dir: 文档存储的基础目录，默认使用配置中的DOCUMENT_STORAGE_PATH
        """
        self.base_dir = base_dir or os.path.join(settings.BASE_DIR, "data", "documents")
        self._ensure_dir_exists(self.base_dir)
        self.metadata_path = os.path.join(self.base_dir, "metadata.json")
        self.metadata = self._load_metadata()
        
    def _ensure_dir_exists(self, path: str) -> None:
        """确保目录存在，不存在则创建"""
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
    def _load_metadata(self) -> Dict:
        """加载文档元数据"""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载文档元数据失败: {e}")
                return {"documents": {}}
        else:
            return {"documents": {}}
            
    def _save_metadata(self) -> None:
        """保存文档元数据"""
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存文档元数据失败: {e}")
            
    def save_document(self, file: BinaryIO, filename: str, user_id: str = "guest") -> Dict:
        """保存文档
        
        Args:
            file: 文件对象
            filename: 文件名
            user_id: 用户ID，默认为guest
            
        Returns:
            文档元数据
        """
        # 生成唯一文档ID
        doc_id = str(uuid.uuid4())
        
        # 创建用户目录
        user_dir = os.path.join(self.base_dir, user_id)
        self._ensure_dir_exists(user_dir)
        
        # 确定文件扩展名
        _, ext = os.path.splitext(filename)
        if not ext:
            ext = ".txt"
            
        # 保存文件
        storage_path = os.path.join(user_dir, f"{doc_id}{ext}")
        with open(storage_path, 'wb') as f:
            shutil.copyfileobj(file, f)
            
        # 更新元数据
        now = datetime.now().isoformat()
        document_metadata = {
            "id": doc_id,
            "filename": filename,
            "original_name": filename,
            "storage_path": storage_path,
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
            "size": os.path.getsize(storage_path),
            "status": "uploaded"
        }
        
        # 更新全局元数据
        if "documents" not in self.metadata:
            self.metadata["documents"] = {}
        self.metadata["documents"][doc_id] = document_metadata
        self._save_metadata()
        
        return document_metadata
        
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """获取文档元数据
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档元数据，不存在则返回None
        """
        return self.metadata.get("documents", {}).get(doc_id)
        
    def get_document_content(self, doc_id: str) -> Optional[str]:
        """获取文档内容
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档内容，不存在则返回None
        """
        doc_metadata = self.get_document(doc_id)
        if not doc_metadata:
            return None
            
        storage_path = doc_metadata["storage_path"]
        if not os.path.exists(storage_path):
            return None
            
        try:
            with open(storage_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试以二进制方式读取
            try:
                with open(storage_path, 'rb') as f:
                    return f.read().decode('utf-8', errors='ignore')
            except Exception as e:
                logger.error(f"读取文档内容失败: {e}")
                return None
        except Exception as e:
            logger.error(f"读取文档内容失败: {e}")
            return None
            
    def get_user_documents(self, user_id: str) -> List[Dict]:
        """获取用户的所有文档
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户的所有文档元数据列表
        """
        user_docs = []
        for doc_id, metadata in self.metadata.get("documents", {}).items():
            if metadata.get("user_id") == user_id:
                user_docs.append(metadata)
        
        # 按更新时间排序
        user_docs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return user_docs
        
    def update_document_status(self, doc_id: str, status: str, task_id: str = None) -> Optional[Dict]:
        """更新文档状态
        
        Args:
            doc_id: 文档ID
            status: 文档状态
            task_id: 任务ID，可选
            
        Returns:
            更新后的文档元数据，不存在则返回None
        """
        doc_metadata = self.get_document(doc_id)
        if not doc_metadata:
            return None
            
        doc_metadata["status"] = status
        doc_metadata["updated_at"] = datetime.now().isoformat()
        if task_id:
            doc_metadata["task_id"] = task_id
            
        self.metadata["documents"][doc_id] = doc_metadata
        self._save_metadata()
        
        return doc_metadata
        
    def delete_document(self, doc_id: str) -> bool:
        """删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        doc_metadata = self.get_document(doc_id)
        if not doc_metadata:
            return False
            
        # 删除文件
        storage_path = doc_metadata["storage_path"]
        if os.path.exists(storage_path):
            try:
                os.remove(storage_path)
            except Exception as e:
                logger.error(f"删除文档文件失败: {e}")
                return False
                
        # 更新元数据
        self.metadata["documents"].pop(doc_id, None)
        self._save_metadata()
        
        return True
        
    def link_document_to_graph(self, doc_id: str, graph_id: str) -> Optional[Dict]:
        """将文档与图谱关联
        
        Args:
            doc_id: 文档ID
            graph_id: 图谱ID
            
        Returns:
            更新后的文档元数据，不存在则返回None
        """
        doc_metadata = self.get_document(doc_id)
        if not doc_metadata:
            return None
            
        if "graphs" not in doc_metadata:
            doc_metadata["graphs"] = []
            
        if graph_id not in doc_metadata["graphs"]:
            doc_metadata["graphs"].append(graph_id)
            
        doc_metadata["updated_at"] = datetime.now().isoformat()
        self.metadata["documents"][doc_id] = doc_metadata
        self._save_metadata()
        
        return doc_metadata

# 创建单例
document_storage = DocumentStorage() 