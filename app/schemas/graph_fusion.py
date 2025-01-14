from pydantic import BaseModel
from typing import List, Dict, Tuple

class FuseGraphRequest(BaseModel):
    triples: List[Tuple[str, str, str]]
    annotated_triples: List[Tuple[str, str, str]]


class FuseGraphResponse(BaseModel):
    fused_triples: List[Dict[str, str]]