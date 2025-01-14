from pydantic import BaseModel
from typing import List, Dict

class ExtractRelationsRequest(BaseModel):
    text: str
    concepts: List[str]

class ExtractRelationsResponse(BaseModel):
    triples: List[Dict[str, str]]