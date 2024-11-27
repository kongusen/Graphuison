from pydantic import BaseModel
from typing import List, Dict, Any

class TextInput(BaseModel):
    texts: List[str]
    stop_words: List[str] = None
    config: Dict[str, Any] = None

class TripleExtractionInput(BaseModel):
    data: Dict[str, Dict[str, List[str]]]
    relation_def: Dict[str, Dict[str, str]]
    config: Dict[str, Any]

class FusionInput(BaseModel):
    candidate_triples: List[Dict[str, str]]
    data: Dict[str, Dict[str, List[str]]]
    relation_def: Dict[str, Dict[str, str]]
    config: Dict[str, Any]