import pytest
import asyncio
from backend.app.models.llm_chain import LLMChain
from backend.app.utils.exceptions import LLMException
from backend.app.config import LlamaSettings
from llama_index.llms.openai import OpenAI

@pytest.mark.asyncio
async def test_query_llm_valid():
     llm_chain = LLMChain()
     prompt="test"
     result = await llm_chain.query_llm(prompt)
     assert isinstance(result,str)

@pytest.mark.asyncio
async def test_query_llm_invalid():
    llm = OpenAI(model=LlamaSettings.LLM_MODEL, api_key=LlamaSettings.OPENAI_API_KEY,api_base=LlamaSettings.OPENAI_BASE_URL)
    llm_chain = LLMChain()
    prompt="Extract triples from given text but it is empty"
    with pytest.raises(LLMException):
      await llm_chain.query_llm(prompt)