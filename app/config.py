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

load_dotenv()


class AppSettings(BaseSettings):
    # 日志配置
    LOG_FILE: str = "app.log"

    # 模型配置
    RELATION_EXTRACTION_MODEL: str = "bert-base-uncased"
    LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    DEVICE: str = "cpu"
    EMBED_MODEL_NAME: str = "text-embedding-3-small"
    TOKENIZER_MODEL: str = "gpt-4o-mini" # 用于tokenizer
    TRANSFORMATIONS_CHUNK_SIZE:int = 1024
    CONTEXT_WINDOW: int = 4096
    NUM_OUTPUT: int = 256
    CHUNK_SIZE : int = 512
    CHUNK_OVERLAP: int = 20
    LANGUAGE : str = os.getenv("LANGUAGE","en")
    DEFAULT_LANGUAGE:str = "en"
    ENABLE_LLM_SPECIAL_TERMS: bool = False # 是否开启大模型获取专有名词
    SPECIAL_TERMS_PATH: str = "special_terms.json" # 专有名词存储路径
    API_PORT: int = "8000"

    # 数据配置
    RELATION_DEFINITIONS: dict = {
        "isA": "The subject is a type or instance of the object.",
        "partOf": "The subject is a part or component of the object.",
        "locatedIn": "The subject is physically located within the object.",
         "uses":"The subject use the object",
        "compare":"The subject and object is comparable",
        "connected":"The subject and object is connected",
        # 添加更多关系定义...
    }

    # 提示模板配置
    TEMPLATES: dict = {
        "relation_extraction": "Extract triples in the format: \n\nSUBJECT (SUBJECT_TYPE), RELATION, OBJECT (OBJECT_TYPE) \n if they exist in current context. otherwise please provide no.",
        "graph_fusion": "Fuse the candidate triples with the prior knowledge graph and output the merged triples in the format: \n\nSUBJECT (SUBJECT_TYPE), RELATION, OBJECT (OBJECT_TYPE)\n if they exist in current context. otherwise please provide no.",
        # 添加更多提示模板...
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