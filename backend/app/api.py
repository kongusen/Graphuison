from fastapi import FastAPI
from app.routers import knowledge_graph, chat, auth
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.utils.database import neo4j_client
from app.utils.redis import init_redis
from app.utils.background_tasks import init_background_tasks
from fastapi.openapi.docs import get_swagger_ui_html
from typing import List, Dict
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 确保数据目录存在
os.makedirs(os.path.join(settings.BASE_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(settings.BASE_DIR, "data", "documents"), exist_ok=True)
os.makedirs(os.path.join(settings.BASE_DIR, "data", "graphs"), exist_ok=True)
os.makedirs(os.path.join(settings.BASE_DIR, "data", "users"), exist_ok=True)

app = FastAPI(
    title="Graphuison - 知识图谱构建与应用平台",
    description="基于多粒度知识融合的智能知识图谱平台，支持文档上传、知识抽取、图谱生成与查询。",
    version="1.0.0",
    docs_url=None,  # 禁用默认文档
    redoc_url=None  # 禁用默认redoc
)

# 支持跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(knowledge_graph.router, prefix="/kg", tags=["知识图谱管理"])
app.include_router(chat.router, prefix="/chat", tags=["智能问答"])
app.include_router(auth.router, prefix="/auth", tags=["用户认证"])

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    try:
        # 初始化 Redis
        init_redis()
        # 初始化后台任务
        init_background_tasks()
        logger.info("应用启动成功")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    try:
        # 关闭后台任务
        from app.utils.background_tasks import background_tasks
        background_tasks.stop()
        logger.info("应用关闭成功")
    except Exception as e:
        logger.error(f"应用关闭失败: {e}")

@app.get("/", tags=["系统信息"])
def read_root():
    """获取系统基本信息"""
    return {
        "name": "Graphuison 知识图谱平台",
        "version": "1.0.0",
        "description": "基于多粒度知识融合的智能知识图谱平台"
    }

# 自定义Swagger API文档
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义API文档界面"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Graphuison API文档",
    )

@app.get("/graph/all", tags=["知识图谱查询"])
async def get_graph_data():
    """获取完整的知识图谱数据"""
    try:
        neo4j_client.connect()
        data = neo4j_client.get_graph_data()
        neo4j_client.close()
        return data
    except Exception as e:
        logger.error(f"获取图谱数据失败: {e}")
        return {"error": str(e)}

@app.get("/stats", tags=["系统信息"])
async def get_stats():
    """获取知识图谱统计信息"""
    try:
        neo4j_client.connect()
        graph_data = neo4j_client.get_graph_data()
        
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
        
        return {
            "entities_count": len(entities),
            "triples_count": triples,
            "relation_types_count": len(relation_types),
            "granularity_stats": granularity_stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return {"error": str(e)}

@app.delete("/graph/clear", tags=["知识图谱管理"])
async def clear_graph_data():
    """清空知识图谱数据"""
    try:
        neo4j_client.connect()
        neo4j_client.clear_database()
        neo4j_client.close()
        return {"message": "知识图谱数据已清空"}
    except Exception as e:
        logger.error(f"清空图谱数据失败: {e}")
        return {"error": str(e)}