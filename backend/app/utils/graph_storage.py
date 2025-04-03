# backend/app/utils/graph_storage.py
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging
from app.config import settings
from app.utils.database import neo4j_client

logger = logging.getLogger(__name__)

class GraphStorage:
    """图谱存储管理类"""
    
    def __init__(self, base_dir: str = None):
        """初始化图谱存储
        
        Args:
            base_dir: 图谱元数据存储的基础目录，默认使用配置中的GRAPH_STORAGE_PATH
        """
        self.base_dir = base_dir or os.path.join(settings.BASE_DIR, "data", "graphs")
        self._ensure_dir_exists(self.base_dir)
        self.metadata_path = os.path.join(self.base_dir, "metadata.json")
        self.metadata = self._load_metadata()
        
    def _ensure_dir_exists(self, path: str) -> None:
        """确保目录存在，不存在则创建"""
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
    def _load_metadata(self) -> Dict:
        """加载图谱元数据"""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载图谱元数据失败: {e}")
                return {"graphs": {}}
        else:
            return {"graphs": {}}
            
    def _save_metadata(self) -> None:
        """保存图谱元数据"""
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存图谱元数据失败: {e}")
            
    def create_graph(self, name: str, description: str, user_id: str, doc_id: str = None) -> Dict:
        """创建图谱记录
        
        Args:
            name: 图谱名称
            description: 图谱描述
            user_id: 用户ID
            doc_id: 关联的文档ID，可选
            
        Returns:
            图谱元数据
        """
        # 生成唯一图谱ID
        graph_id = str(uuid.uuid4())
        
        # 更新元数据
        now = datetime.now().isoformat()
        graph_metadata = {
            "id": graph_id,
            "name": name,
            "description": description,
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
            "status": "created",
            "stats": {
                "entities_count": 0,
                "triples_count": 0,
                "relation_types_count": 0,
                "granularity_stats": {
                    "fine": 0,
                    "medium": 0,
                    "coarse": 0,
                    "cross_granularity": 0
                }
            }
        }
        
        # 关联文档
        if doc_id:
            graph_metadata["document_id"] = doc_id
            
        # 更新全局元数据
        if "graphs" not in self.metadata:
            self.metadata["graphs"] = {}
        self.metadata["graphs"][graph_id] = graph_metadata
        self._save_metadata()
        
        return graph_metadata
        
    def get_graph(self, graph_id: str) -> Optional[Dict]:
        """获取图谱元数据
        
        Args:
            graph_id: 图谱ID
            
        Returns:
            图谱元数据，不存在则返回None
        """
        return self.metadata.get("graphs", {}).get(graph_id)
        
    def get_user_graphs(self, user_id: str) -> List[Dict]:
        """获取用户的所有图谱
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户的所有图谱元数据列表
        """
        user_graphs = []
        for graph_id, metadata in self.metadata.get("graphs", {}).items():
            if metadata.get("user_id") == user_id:
                user_graphs.append(metadata)
        
        # 按更新时间排序
        user_graphs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return user_graphs
        
    def update_graph_status(self, graph_id: str, status: str) -> Optional[Dict]:
        """更新图谱状态
        
        Args:
            graph_id: 图谱ID
            status: 图谱状态
            
        Returns:
            更新后的图谱元数据，不存在则返回None
        """
        graph_metadata = self.get_graph(graph_id)
        if not graph_metadata:
            return None
            
        graph_metadata["status"] = status
        graph_metadata["updated_at"] = datetime.now().isoformat()
        self.metadata["graphs"][graph_id] = graph_metadata
        self._save_metadata()
        
        return graph_metadata
        
    def update_graph_stats(self, graph_id: str) -> Optional[Dict]:
        """更新图谱统计信息
        
        Args:
            graph_id: 图谱ID
            
        Returns:
            更新后的图谱元数据，不存在则返回None
        """
        graph_metadata = self.get_graph(graph_id)
        if not graph_metadata:
            return None
            
        try:
            # 从Neo4j获取统计信息
            neo4j_client.connect()
            graph_data = neo4j_client.get_graph_data()
            
            # 统计实体和关系
            entities = set()
            triples = 0
            relation_types = set()
            granularity_stats = {"fine": 0, "medium": 0, "coarse": 0, "cross_granularity": 0}
            
            for item in graph_data:
                entities.add(item['source'])
                entities.add(item['target'])
                relation_types.add(item['relation'])
                triples += 1
                
                # 根据节点类型统计不同粒度的关系数量
                source_type = item.get('source_type', '')
                target_type = item.get('target_type', '')
                
                if source_type and 'fine' in source_type and target_type and 'fine' in target_type:
                    granularity_stats['fine'] += 1
                elif source_type and 'medium' in source_type and target_type and 'medium' in target_type:
                    granularity_stats['medium'] += 1
                elif source_type and 'coarse' in source_type and target_type and 'coarse' in target_type:
                    granularity_stats['coarse'] += 1
                else:
                    granularity_stats['cross_granularity'] += 1
                    
            neo4j_client.close()
            
            # 更新统计信息
            graph_metadata["stats"] = {
                "entities_count": len(entities),
                "triples_count": triples,
                "relation_types_count": len(relation_types),
                "granularity_stats": granularity_stats
            }
            
            graph_metadata["updated_at"] = datetime.now().isoformat()
            self.metadata["graphs"][graph_id] = graph_metadata
            self._save_metadata()
            
            return graph_metadata
            
        except Exception as e:
            logger.error(f"更新图谱统计信息失败: {e}")
            return graph_metadata
            
    def delete_graph(self, graph_id: str) -> bool:
        """删除图谱
        
        Args:
            graph_id: 图谱ID
            
        Returns:
            是否删除成功
        """
        graph_metadata = self.get_graph(graph_id)
        if not graph_metadata:
            return False
            
        # 清空Neo4j中的图数据
        try:
            neo4j_client.connect()
            # TODO: 只删除特定图谱的数据
            neo4j_client.clear_database()
            neo4j_client.close()
        except Exception as e:
            logger.error(f"清空Neo4j数据失败: {e}")
            return False
            
        # 更新元数据
        self.metadata["graphs"].pop(graph_id, None)
        self._save_metadata()
        
        return True
        
    def export_graph_data(self, graph_id: str) -> Optional[Dict]:
        """导出图谱数据
        
        Args:
            graph_id: 图谱ID
            
        Returns:
            图谱数据，包含节点和关系，不存在则返回None
        """
        graph_metadata = self.get_graph(graph_id)
        if not graph_metadata:
            return None
            
        try:
            # 从Neo4j获取图数据
            neo4j_client.connect()
            graph_data = neo4j_client.get_graph_data()
            neo4j_client.close()
            
            # 构建导出数据
            export_data = {
                "metadata": graph_metadata,
                "triples": graph_data
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"导出图谱数据失败: {e}")
            return None

# 创建单例
graph_storage = GraphStorage() 