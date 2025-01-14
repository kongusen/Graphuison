from fastapi import APIRouter, HTTPException
from app.models.topic_modeler import TopicModeler
from app.schemas.concept_extraction import ExtractConceptsRequest, ExtractConceptsResponse
from app.models.embedder import SentenceEmbedder
from app.config import settings
from typing import List
router = APIRouter()

@router.post("/extract", response_model=ExtractConceptsResponse)
async def extract_concepts(request: ExtractConceptsRequest):
    try:
        embed_model = SentenceEmbedder(device=settings.DEVICE)
        model = TopicModeler(embed_model=embed_model,language=settings.LANGUAGE)
        lda_model = model.train_lda(request.sentences)
        concepts = model.get_concepts(lda_model)
        return {"concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))