# backend/app/routers/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.utils.database import neo4j_client
from typing import List, Dict
from backend.app.models.llm_chain import LLMChain

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    triples: List[Dict[str,str]]

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
     try:
         llm_chain = LLMChain()
         result = await llm_chain.query_llm(request.query)
         neo4j_client.connect()
         graph_data = neo4j_client.get_graph_data()
         neo4j_client.close()
         triples = []
         for item in graph_data:
           triples.append(item)
         return {"response":result, "triples": triples}
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

class ChatHistoryResponse(BaseModel):
   history: List[Dict[str,str]]

@router.get("/history", response_model=ChatHistoryResponse)
async def get_history():
      return {"history":[]}