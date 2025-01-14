from fastapi import APIRouter, Query
from backend.app.schemas.graph_fusion import FuseGraphRequest, FuseGraphResponse
from backend.app.models.graph_fusioner import GraphFusioner
from backend.app.config import settings
from typing import List, Optional, Dict, Tuple

router = APIRouter()

graph_fusioner = GraphFusioner(settings.RELATION_DEFINITIONS, settings.TEMPLATES)

@router.post("/fuse",response_model=FuseGraphResponse)
async def fuse_graph(
   triples: List[Tuple[str, str, str]],
   annotated_triples: List[Tuple[str, str, str]],
   page: int = Query(1, ge=1, description="Page number"),
   page_size: int = Query(10, ge=1, le=100, description="Page size"),
) -> dict:
     fused_triples = await graph_fusioner.fuse_graph(triples, annotated_triples)
     start_index = (page - 1) * page_size
     end_index = start_index + page_size
     paginated_triples = fused_triples[start_index:end_index]
     total_count = len(fused_triples)
     return {
             "fused_triples": paginated_triples,
             "page": page,
             "page_size": page_size,
             "total_count": total_count,
             "total_pages": (total_count + page_size - 1) // page_size
         }