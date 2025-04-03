from pydantic_settings import BaseSettings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings as LlamaSettings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.callbacks import TokenCountingHandler, CallbackManager
import tiktoken
from transformers import AutoTokenizer
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from pydantic import Field, validator
from typing import Dict
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# 默认关系定义
DEFAULT_RELATION_DEFINITIONS = {
    "isA": "The subject is a type or instance of the object.",
    "partOf": "The subject is a part or component of the object.",
    "locatedIn": "The subject is physically located within the object.",
    "uses": "The subject use the object",
    "compare": "The subject and object is comparable",
    "connected": "The subject and object is connected"
}

class AppSettings(BaseSettings):
    # 基础配置
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    API_PORT: int = 8000
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"
    LOG_FILE: str = "app.log"
    SECRET_KEY: str = "your_secret_key_please_change_in_production"

    # OpenAI配置
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4"
    EMBED_MODEL_NAME: str = "text-embedding-3-small"
    TOKENIZER_MODEL: str = "gpt-4o-mini"  # 用于tokenizer
    RELATION_EXTRACTION_MODEL: str = "bert-base-uncased"

    # 语言配置
    LANGUAGE: str = "zh"
    DEFAULT_LANGUAGE: str = "en"

    # 数据库配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # 模型配置
    DEVICE: str = "cpu"
    TRANSFORMATIONS_CHUNK_SIZE: int = 1024
    CONTEXT_WINDOW: int = 4096
    NUM_OUTPUT: int = 256
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 20

    # 知识图谱配置
    RELATION_DEFINITIONS: Dict[str, str] = DEFAULT_RELATION_DEFINITIONS
    RELATION_EXTRACTION_TEMPLATE: str = Field(
        default="请分析以下文本，提取其中的实体关系。要求：\n1. 识别主体和客体及其类型\n2. 确定它们之间的关系\n3. 以'主体(类型), 关系, 客体(类型)'的格式输出\n如果没有明确的关系，请返回no。"
    )
    GRAPH_FUSION_TEMPLATE: str = Field(
        default="请将候选三元组与已有知识图谱进行融合。要求：\n1. 检查候选三元组与已有知识的一致性\n2. 处理可能的冲突\n3. 推断新的关系\n4. 以'主体(类型), 关系, 客体(类型)'的格式输出融合后的三元组\n如果没有需要融合的三元组，请返回no。"
    )

    # 特殊功能配置
    ENABLE_LLM_SPECIAL_TERMS: bool = False
    SPECIAL_TERMS_PATH: str = "special_terms.json"

    # 存储路径配置
    DOCUMENT_STORAGE_PATH: str = "./data/documents"
    GRAPH_STORAGE_PATH: str = "./data/graphs"
    USER_STORAGE_PATH: str = "./data/users"

    # 认证配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    TOKEN_ALGORITHM: str = "HS256"

    @validator("RELATION_DEFINITIONS", pre=True)
    def parse_relation_definitions(cls, v):
        """解析关系定义"""
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                # 移除可能的引号和空格
                v = v.strip().strip("'\"")
                return json.loads(v)
            except json.JSONDecodeError as e:
                logger.error(f"解析关系定义失败: {e}")
                return DEFAULT_RELATION_DEFINITIONS
        return DEFAULT_RELATION_DEFINITIONS

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # 允许额外的配置项

    @property
    def TEMPLATES(self) -> Dict[str, str]:
        """获取提示模板"""
        return {
            "relation_extraction": self.RELATION_EXTRACTION_TEMPLATE,
            "graph_fusion": self.GRAPH_FUSION_TEMPLATE
        }

settings = AppSettings()

# 全局配置 llama_index Settings
LlamaSettings.llm = OpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY, api_base=settings.OPENAI_BASE_URL)
LlamaSettings.embed_model = OpenAIEmbedding(
    model=settings.EMBED_MODEL_NAME, embed_batch_size=100, api_key=settings.OPENAI_API_KEY, api_base=settings.OPENAI_BASE_URL
)
LlamaSettings.text_splitter = SentenceSplitter(chunk_size=settings.TRANSFORMATIONS_CHUNK_SIZE)
LlamaSettings.transformations = [SentenceSplitter(chunk_size=settings.TRANSFORMATIONS_CHUNK_SIZE)]
LlamaSettings.tokenizer = tiktoken.encoding_for_model(settings.TOKENIZER_MODEL).encode
token_counter = TokenCountingHandler()
LlamaSettings.callback_manager = CallbackManager([token_counter])
LlamaSettings.context_window = settings.CONTEXT_WINDOW
LlamaSettings.num_output = settings.NUM_OUTPUT
LlamaSettings.chunk_size = settings.CHUNK_SIZE
LlamaSettings.chunk_overlap = settings.CHUNK_OVERLAP