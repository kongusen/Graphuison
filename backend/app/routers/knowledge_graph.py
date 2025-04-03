from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Query, Depends, Form
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging
from app.models.text_processor import TextProcessor
from app.models.topic_modeler import TopicModeler
from app.models.embedder import SentenceEmbedder
from app.models.relation_extractor import RelationExtractor
from app.models.graph_fusioner import GraphFusioner
from app.models.llm_chain import LLMChain
from app.config import settings
from app.utils.database import neo4j_client
from app.utils.auth import get_current_user, get_required_user
from app.utils.redis import redis_client
from app.utils.background_tasks import background_tasks
from app.utils.document_storage import document_storage
from app.utils.graph_storage import graph_storage
import asyncio
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class GraphGenerationStatus(BaseModel):
    status: str
    progress: float
    message: str
    timestamp: datetime
    result: Optional[Dict] = None

class GraphGenerationResponse(BaseModel):
    task_id: str
    graph_id: str
    doc_id: str
    status: str
    message: str

class EntitySearchRequest(BaseModel):
    query: str
    max_results: int = 10

class EntityRelationResponse(BaseModel):
    entity: str
    related_entities: List[Dict]
    relations: List[Dict]

class DocumentInfo(BaseModel):
    id: str
    filename: str
    original_name: str
    size: int
    created_at: str
    updated_at: str
    status: str
    user_id: str
    graphs: Optional[List[str]] = None

class GraphInfo(BaseModel):
    id: str
    name: str
    description: str
    user_id: str
    created_at: str
    updated_at: str
    status: str
    document_id: Optional[str] = None
    stats: Dict

# 存储任务状态
task_status = {}

async def process_document(file_content: str, task_id: str, doc_id: str, graph_id: str, user_id: str):
    """后台处理文档并生成知识图谱"""
    try:
        task_status[task_id] = {
            "status": "processing",
            "progress": 0.0,
            "message": "开始处理文档...",
            "timestamp": datetime.now()
        }
        
        # 更新文档状态
        document_storage.update_document_status(doc_id, "processing", task_id)
        
        # 更新图谱状态
        graph_storage.update_graph_status(graph_id, "processing")
        
        # 1. 文本预处理
        processor = TextProcessor(language=settings.LANGUAGE)
        sentences, _ = await processor.preprocess_text(file_content)
        task_status[task_id]["progress"] = 0.2
        task_status[task_id]["message"] = "文本预处理完成"
        
        # 2. 概念提取
        embed_model = SentenceEmbedder(device=settings.DEVICE)
        topic_model = TopicModeler(embed_model=embed_model, language=settings.LANGUAGE)
        
        # 提取不同粒度的概念
        concepts = {}
        for level in topic_model.topic_levels.keys():
            level_concepts = await topic_model.get_concepts(sentences, granularity=level)
            concepts[level] = level_concepts
        
        task_status[task_id]["progress"] = 0.4
        task_status[task_id]["message"] = "多粒度概念提取完成"
        
        # 3. 关系提取
        llm_chain = LLMChain()
        extractor = RelationExtractor(
            model_name=settings.RELATION_EXTRACTION_MODEL,
            relation_defs=settings.RELATION_DEFINITIONS,
            templates=settings.TEMPLATES,
            llm_chain=llm_chain
        )
        
        # 对每个粒度级别的概念提取关系
        all_triples = {}
        for level, level_concepts in concepts.items():
            level_triples = await extractor.extract_relations(file_content, level_concepts)
            all_triples[level] = level_triples
        
        task_status[task_id]["progress"] = 0.6
        task_status[task_id]["message"] = "多粒度关系提取完成"
        
        # 4. 图融合
        graph_fusioner = GraphFusioner(settings.RELATION_DEFINITIONS, settings.TEMPLATES)
        
        # 将所有三元组作为多粒度数据传递给图融合器
        fused_graphs = await graph_fusioner.fuse_graph(all_triples)
        
        task_status[task_id]["progress"] = 0.8
        task_status[task_id]["message"] = "多粒度图融合完成"
        
        # 5. 保存到数据库
        neo4j_client.connect()
        
        # 清空现有数据库（可选，取决于需求）
        # neo4j_client.clear_database()
        
        # 保存各粒度级别的三元组
        for level, level_triples in fused_graphs.items():
            for s, r, o in level_triples:
                try:
                    source_id = neo4j_client.create_node(s, f'entity_{level}')
                    target_id = neo4j_client.create_node(o, f'entity_{level}')
                    if source_id and target_id:
                        neo4j_client.create_relationship(source_id, target_id, r)
                except Exception as e:
                    logger.error(f"Error saving triple ({s}, {r}, {o}): {e}")
        
        neo4j_client.close()
        
        # 更新任务状态
        task_status[task_id].update({
            "status": "completed",
            "progress": 1.0,
            "message": "知识图谱生成完成",
            "timestamp": datetime.now(),
            "result": {
                "concepts": concepts,
                "triples": all_triples,
                "fused_graphs": fused_graphs
            }
        })
        
        # 更新文档状态
        document_storage.update_document_status(doc_id, "processed", task_id)
        
        # 更新图谱状态和统计信息
        graph_storage.update_graph_status(graph_id, "completed")
        graph_storage.update_graph_stats(graph_id)
        
        # 关联文档和图谱
        document_storage.link_document_to_graph(doc_id, graph_id)
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        task_status[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": f"处理失败: {str(e)}",
            "timestamp": datetime.now()
        })
        
        # 更新文档状态
        document_storage.update_document_status(doc_id, "failed", task_id)
        
        # 更新图谱状态
        graph_storage.update_graph_status(graph_id, "failed")

@router.post("/upload", response_model=GraphGenerationResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    current_user: Dict = Depends(get_required_user)
):
    """上传文档并开始生成知识图谱"""
    try:
        user_id = current_user["id"]
        
        # 1. 保存文档
        content = await file.read()
        doc_metadata = document_storage.save_document(content, file.filename, user_id)
        
        # 2. 创建图谱记录
        graph_metadata = graph_storage.create_graph(name, description, user_id, doc_metadata["id"])
        
        # 生成任务ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 获取文档内容（字符串）
        content_str = content.decode('utf-8', errors='ignore')
        
        # 启动后台任务
        background_tasks.add_task(
            process_document, 
            content_str, 
            task_id, 
            doc_metadata["id"], 
            graph_metadata["id"],
            user_id
        )
        
        return {
            "task_id": task_id,
            "graph_id": graph_metadata["id"],
            "doc_id": doc_metadata["id"],
            "status": "processing",
            "message": "文档上传成功，开始处理"
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}", response_model=GraphGenerationStatus)
async def get_status(task_id: str, current_user: Dict = Depends(get_required_user)):
    """获取任务处理状态"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_status[task_id]

@router.get("/result/{task_id}")
async def get_result(task_id: str, current_user: Dict = Depends(get_required_user)):
    """获取处理结果"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = task_status[task_id]
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    return status["result"]

@router.get("/search", response_model=List[Dict])
async def search_entities(
    query: str, 
    max_results: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """搜索知识图谱中的实体"""
    try:
        neo4j_client.connect()
        # 使用模糊匹配搜索实体
        search_query = f"""
            MATCH (n:Entity)
            WHERE n.name CONTAINS $query
            RETURN n.name as name, n.type as type
            LIMIT $max_results
        """
        with neo4j_client.driver.session() as session:
            result = session.run(search_query, query=query, max_results=max_results)
            entities = [{"name": record["name"], "type": record["type"]} for record in result]
        
        neo4j_client.close()
        return entities
    except Exception as e:
        logger.error(f"实体搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entity/{entity_name}", response_model=EntityRelationResponse)
async def get_entity_relations(
    entity_name: str, 
    depth: int = Query(1, ge=1, le=3),
    current_user: Dict = Depends(get_current_user)
):
    """获取指定实体的关系信息"""
    try:
        neo4j_client.connect()
        
        # 获取实体信息
        entity = neo4j_client.get_entity_by_name(entity_name)
        if not entity:
            neo4j_client.close()
            raise HTTPException(status_code=404, detail=f"实体 '{entity_name}' 未找到")
        
        # 获取与该实体相关的实体
        related_entities = neo4j_client.find_related_entities(entity_name, depth)
        
        # 获取该实体的所有关系
        relations_query = """
            MATCH (source:Entity {name: $entity_name})-[r]->(target:Entity)
            RETURN source.name as source, type(r) as relation, target.name as target,
                   source.type as source_type, target.type as target_type
            UNION
            MATCH (source:Entity)-[r]->(target:Entity {name: $entity_name})
            RETURN source.name as source, type(r) as relation, target.name as target,
                   source.type as source_type, target.type as target_type
        """
        with neo4j_client.driver.session() as session:
            result = session.run(relations_query, entity_name=entity_name)
            relations = [
                {
                    "source": record["source"],
                    "relation": record["relation"],
                    "target": record["target"],
                    "source_type": record["source_type"],
                    "target_type": record["target_type"]
                }
                for record in result
            ]
        
        neo4j_client.close()
        
        return {
            "entity": entity_name,
            "related_entities": related_entities,
            "relations": relations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取实体关系失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/granularity/{level}")
async def get_graph_by_granularity(level: str, current_user: Dict = Depends(get_current_user)):
    """获取特定粒度级别的知识图谱"""
    if level not in ["fine", "medium", "coarse", "cross_granularity", "all"]:
        raise HTTPException(status_code=400, detail="无效的粒度级别。有效值: fine, medium, coarse, cross_granularity, all")
    
    try:
        neo4j_client.connect()
        
        if level == "all":
            # 获取所有图谱数据
            data = neo4j_client.get_graph_data()
        else:
            # 构建查询特定粒度级别的Cypher查询
            query = """
                MATCH (source:Entity)-[r:Relationship]->(target:Entity)
                WHERE source.type CONTAINS $level OR target.type CONTAINS $level
                RETURN source.name as source, type(r) as relation, target.name as target,
                       source.type as source_type, target.type as target_type
            """
            with neo4j_client.driver.session() as session:
                result = session.run(query, level=f"entity_{level}")
                data = [
                    {
                        "source": record["source"],
                        "relation": record["relation"],
                        "target": record["target"],
                        "source_type": record["source_type"],
                        "target_type": record["target_type"]
                    }
                    for record in result
                ]
        
        neo4j_client.close()
        return data
    except Exception as e:
        logger.error(f"获取粒度级别图谱失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[DocumentInfo])
async def get_user_documents(current_user: Dict = Depends(get_required_user)):
    """获取当前用户的所有文档"""
    user_id = current_user["id"]
    documents = document_storage.get_user_documents(user_id)
    return documents

@router.get("/documents/{doc_id}", response_model=DocumentInfo)
async def get_document(doc_id: str, current_user: Dict = Depends(get_required_user)):
    """获取文档信息"""
    doc = document_storage.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # 验证所有权
    if doc["user_id"] != current_user["id"] and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="无权访问此文档")
        
    return doc

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, current_user: Dict = Depends(get_required_user)):
    """删除文档"""
    doc = document_storage.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # 验证所有权
    if doc["user_id"] != current_user["id"] and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="无权删除此文档")
        
    result = document_storage.delete_document(doc_id)
    if not result:
        raise HTTPException(status_code=500, detail="删除文档失败")
        
    return {"message": "文档已删除"}

@router.get("/graphs", response_model=List[GraphInfo])
async def get_user_graphs(current_user: Dict = Depends(get_required_user)):
    """获取当前用户的所有知识图谱"""
    user_id = current_user["id"]
    graphs = graph_storage.get_user_graphs(user_id)
    return graphs

@router.get("/graphs/{graph_id}", response_model=GraphInfo)
async def get_graph(graph_id: str, current_user: Dict = Depends(get_required_user)):
    """获取图谱信息"""
    graph = graph_storage.get_graph(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
        
    # 验证所有权
    if graph["user_id"] != current_user["id"] and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="无权访问此图谱")
        
    return graph

@router.delete("/graphs/{graph_id}")
async def delete_graph(graph_id: str, current_user: Dict = Depends(get_required_user)):
    """删除图谱"""
    graph = graph_storage.get_graph(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
        
    # 验证所有权
    if graph["user_id"] != current_user["id"] and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="无权删除此图谱")
        
    result = graph_storage.delete_graph(graph_id)
    if not result:
        raise HTTPException(status_code=500, detail="删除图谱失败")
        
    return {"message": "图谱已删除"}

@router.get("/graphs/{graph_id}/export")
async def export_graph(graph_id: str, current_user: Dict = Depends(get_required_user)):
    """导出图谱数据"""
    graph = graph_storage.get_graph(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
        
    # 验证所有权
    if graph["user_id"] != current_user["id"] and not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="无权导出此图谱")
        
    export_data = graph_storage.export_graph_data(graph_id)
    if not export_data:
        raise HTTPException(status_code=500, detail="导出图谱数据失败")
        
    return export_data 