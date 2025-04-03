# backend/app/models/llm_chain.py
import os
import asyncio
from llama_index.core import Settings, VectorStoreIndex, StorageContext, load_index_from_storage, SimpleDirectoryReader
from app.utils.exceptions import LLMException
from typing import Optional
from app.config import LlamaSettings
import logging

logger = logging.getLogger(__name__)

class LLMChain:
    def __init__(self):
        self.persist_dir = "./storage"
        self.index = self._load_or_create_index()

    def _load_or_create_index(self):
        if not os.path.exists(self.persist_dir):
            # 如目录不存在，加载文档并创建索引
            try:
                documents = SimpleDirectoryReader("data").load_data()
                index = VectorStoreIndex.from_documents(documents, service_context=LlamaSettings)
                # 持久化存储以备后用
                index.storage_context.persist(persist_dir=self.persist_dir)
                return index
            except Exception as e:
                logger.error(f"Error loading or creating index: {e}")
                return None
        else:
            # 加载已有索引
            try:
                storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
                index = load_index_from_storage(storage_context)
                return index
            except Exception as e:
                logger.error(f"Error loading existing index: {e}")
                return None
    async def query_llm(self, prompt: str, chunk_size: Optional[int] = None) -> str:
        # 使用现有索引进行查询
        query_engine = self.index.as_query_engine()
        try:
            response = await asyncio.get_running_loop().run_in_executor(None, query_engine.query, "Query the information from given knowledge" + prompt)
            return response.response
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise LLMException(f"LLM call failed: {e}") from e