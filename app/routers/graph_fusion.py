from fastapi import APIRouter, HTTPException
from typing import List
from app.models.graph_fusioner import GraphFusioner
from app.schemas.graph_fusion import FuseGraphRequest, FuseGraphResponse
from app.models.llm_chain import LLMChain
from app.config import settings

router = APIRouter()

@router.post("/fuse", response_model=FuseGraphResponse)
async def fuse_graph(request: FuseGraphRequest):
    try:
        llm_chain = LLMChain()
        fusioner = GraphFusioner(
            relation_defs=settings.RELATION_DEFINITIONS,
            templates=settings.TEMPLATES,
            llm_chain=llm_chain
        )
        fused_triples = await fusioner.fuse_graph(request.triples, request.annotated_triples)
        return {"fused_triples": [{"subject": s, "relation": r, "object": o} for s, r, o in fused_triples]}
    except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))