# backend/app/routers/chat.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.app.utils.database import neo4j_client
from typing import List, Dict, Optional
from backend.app.models.llm_chain import LLMChain
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    preferred_granularity: Optional[str] = None  # fine, medium, coarse

class ChatResponse(BaseModel):
    response: str
    triples: List[Dict[str, str]]
    relevant_entities: List[Dict]
    granularity_used: str

class ChatHistoryItem(BaseModel):
    id: str
    query: str
    response: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    history: List[ChatHistoryItem]

# 存储聊天历史
chat_history = []

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """基于多粒度知识图谱的智能聊天"""
    try:
        query = request.query
        preferred_granularity = request.preferred_granularity
        
        # 记录请求
        logger.info(f"收到聊天请求: {query}")
        
        # 从查询中提取关键词
        # 这里可以使用 jieba 等工具提取关键词
        # 简单实现：将查询分词
        keywords = query.split()
        
        # 连接数据库
        neo4j_client.connect()
        
        # 查找相关实体
        relevant_entities = []
        for keyword in keywords:
            if len(keyword) >= 2:  # 忽略过短的词
                search_query = f"""
                    MATCH (n:Entity)
                    WHERE n.name CONTAINS $keyword
                    RETURN n.name as name, n.type as type
                    LIMIT 5
                """
                with neo4j_client.driver.session() as session:
                    result = session.run(search_query, keyword=keyword)
                    entities = [{"name": record["name"], "type": record["type"]} for record in result]
                    relevant_entities.extend(entities)
        
        # 根据用户偏好选择粒度，如果没有指定，智能选择
        granularity_used = preferred_granularity
        if not granularity_used:
            # 根据查询复杂度自动选择粒度
            if len(query) < 10:
                granularity_used = "coarse"  # 简短查询使用粗粒度
            elif len(query) < 30:
                granularity_used = "medium"  # 中等长度查询使用中粒度
            else:
                granularity_used = "fine"    # 长查询使用细粒度
        
        # 获取相关的三元组
        triples = []
        if relevant_entities:
            # 创建搜索条件
            entity_names = [entity["name"] for entity in relevant_entities[:5]]  # 限制数量
            
            # 基于相关实体查询相关的三元组，优先使用选定的粒度级别
            triples_query = f"""
                MATCH (source:Entity)-[r:Relationship]->(target:Entity)
                WHERE source.name IN $entity_names OR target.name IN $entity_names
                RETURN source.name as source, type(r) as relation, target.name as target,
                       source.type as source_type, target.type as target_type
                ORDER BY 
                    CASE WHEN source.type CONTAINS $preferred_level OR target.type CONTAINS $preferred_level 
                    THEN 0 ELSE 1 END
                LIMIT 20
            """
            with neo4j_client.driver.session() as session:
                result = session.run(triples_query, 
                                     entity_names=entity_names, 
                                     preferred_level=f"entity_{granularity_used}")
                triples = [
                    {
                        "source": record["source"],
                        "relation": record["relation"],
                        "target": record["target"],
                        "source_type": record["source_type"],
                        "target_type": record["target_type"]
                    }
                    for record in result
                ]
        
        # 如果找不到相关三元组，尝试获取更通用的知识
        if not triples:
            general_query = """
                MATCH (source:Entity)-[r:Relationship]->(target:Entity)
                RETURN source.name as source, type(r) as relation, target.name as target,
                       source.type as source_type, target.type as target_type
                LIMIT 10
            """
            with neo4j_client.driver.session() as session:
                result = session.run(general_query)
                triples = [
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
        
        # 生成回答的提示
        prompt = f"问题: {query}\n\n相关知识:\n"
        for triple in triples:
            prompt += f"{triple['source']} {triple['relation']} {triple['target']}\n"
        
        prompt += "\n根据上述知识，请简明扼要地回答问题。如果知识库中没有相关信息，请诚实说明。"
        
        # 调用LLM生成回答
        llm_chain = LLMChain()
        result = await llm_chain.query_llm(prompt)
        
        # 存储聊天历史
        chat_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        chat_history.append({
            "id": chat_id,
            "query": query,
            "response": result,
            "timestamp": datetime.now()
        })
        
        # 只保留最近50条历史记录
        if len(chat_history) > 50:
            chat_history.pop(0)
        
        return {
            "response": result,
            "triples": triples,
            "relevant_entities": relevant_entities,
            "granularity_used": granularity_used
        }
    except Exception as e:
        logger.error(f"聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=ChatHistoryResponse)
async def get_history(limit: int = Query(10, ge=1, le=50)):
    """获取聊天历史"""
    try:
        recent_history = chat_history[-limit:] if limit < len(chat_history) else chat_history
        return {"history": recent_history}
    except Exception as e:
        logger.error(f"获取聊天历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history")
async def clear_history():
    """清空聊天历史"""
    try:
        chat_history.clear()
        return {"message": "聊天历史已清空"}
    except Exception as e:
        logger.error(f"清空聊天历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))