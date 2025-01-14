from fastapi import FastAPI, Query
from app.routers import text_processing, concept_extraction, relation_extraction, graph_fusion
from app.utils.logger import setup_logger
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from typing import List, Optional, Dict, Tuple

app = FastAPI(
    title="Knowledge Graph Construction API",
    description="An API for constructing knowledge graphs from unstructured text data.",
    version="1.0.0",
    docs_url=None,  # Disable the default doc
    redoc_url=None  # Disable the default redoc
)

# 配置日志
setup_logger(settings.LOG_FILE)

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
app.include_router(relation_extraction.router, prefix="/relations", tags=["Relation Extraction"])
app.include_router(graph_fusion.router, prefix="/graph", tags=["Knowledge Graph Fusion"])


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