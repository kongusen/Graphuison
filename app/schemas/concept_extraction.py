from pydantic import BaseModel
from typing import List

class ExtractConceptsRequest(BaseModel):
    sentences: List[str]

class ExtractConceptsResponse(BaseModel):
     concepts: List[str]