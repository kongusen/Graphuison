from pydantic import BaseModel
from typing import List

class ProcessTextRequest(BaseModel):
    text: str

class ProcessTextResponse(BaseModel):
    sentences: List[str]
    tokens: List[List[str]]

class ProcessFilesRequest(BaseModel):
    file_paths: List[str]