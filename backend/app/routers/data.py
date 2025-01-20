# backend/app/routers/data.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from backend.app.models.text_processor import TextProcessor
from backend.app.config import settings
from backend.app.models.topic_modeler import TopicModeler
from backend.app.models.embedder import SentenceEmbedder
from backend.app.models.relation_extractor import RelationExtractor
from backend.app.models.llm_chain import LLMChain
from pydantic import BaseModel
router = APIRouter()
class UploadResponse(BaseModel):
     triples: List[dict]
@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
     try:
        processor = TextProcessor(language=settings.LANGUAGE)
        text = (await file.read()).decode()
        sentences, _ = await processor.preprocess_text(text)
        embed_model = SentenceEmbedder(device=settings.DEVICE)
        topic_model = TopicModeler(embed_model=embed_model, language=settings.LANGUAGE)
        concepts = await topic_model.get_concepts(sentences)
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