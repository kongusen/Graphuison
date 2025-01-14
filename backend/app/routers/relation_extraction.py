from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
from app.models.relation_extractor import RelationExtractor
from app.schemas.relation_extraction import ExtractRelationsRequest, ExtractRelationsResponse
from app.models.llm_chain import LLMChain
from app.config import settings
import json

router = APIRouter()

@router.post("/extract", response_model=ExtractRelationsResponse)
async def extract_relations(concepts:List[str], file: UploadFile = File(...)):
    try:
         text = (await file.read()).decode()
         llm_chain = LLMChain()
         extractor = RelationExtractor(
            model_name=settings.RELATION_EXTRACTION_MODEL,
            relation_defs=settings.RELATION_DEFINITIONS,
            templates=settings.TEMPLATES,
            llm_chain=llm_chain
         )
         triples = await extractor.extract_relations(text, concepts)
         return {"triples": [{"subject": s, "relation": r, "object": o} for s, r, o in triples]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))