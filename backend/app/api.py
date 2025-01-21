from fastapi import FastAPI, Query
from backend.app.routers import text_processing, concept_extraction, relation_extraction, graph_fusion
from backend.app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.utils.database import neo4j_client
from fastapi.openapi.docs import get_swagger_ui_html
from backend.app.routers import chat
from typing import List, Optional, Dict, Tuple

app = FastAPI(
    title="Knowledge Graph Construction API",
    description="An API for constructing knowledge graphs from unstructured text data.",
    version="1.0.0",
    docs_url=None,  # Disable the default doc
    redoc_url=None  # Disable the default redoc
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
app.include_router(text_processing.router, prefix="/text", tags=["Text Processing"])
app.include_router(concept_extraction.router, prefix="/concepts", tags=["Concept Extraction"])
# app.include_router(relation_extraction.router, prefix="/relations", tags=["Relation Extraction"])
app.include_router(graph_fusion.router, prefix="/graph", tags=["Knowledge Graph Fusion"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Knowledge Graph Construction API!"}


# Custom swagger API docs
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Knowledge Graph Construction API",
    )

# 将融合后的图谱数据写入 Neo4j 数据库
@app.get("/graph/all", tags=["Knowledge Graph Fusion"])
async def get_graph_data():
    neo4j_client.connect()
    data = neo4j_client.get_graph_data()
    neo4j_client.close()
    return data

# 用于返回知识图谱的统计信息
@app.get("/stats", tags=["Stats"])
async def get_stats():
    neo4j_client.connect()
    graph_data = neo4j_client.get_graph_data()
    neo4j_client.close()
    entities = set()
    triples = 0
    for item in graph_data:
      entities.add(item['source'])
      entities.add(item['target'])
      triples += 1
    return {
         "entities_count": len(entities),
         "triples_count": triples
         }