from fastapi import APIRouter, HTTPException
from backend.app.models.topic_modeler import TopicModeler
from backend.app.schemas.concept_extraction import ExtractConceptsRequest, ExtractConceptsResponse
from backend.app.models.embedder import SentenceEmbedder
from backend.app.config import settings
from typing import List

router = APIRouter()


@router.post("/extract", response_model=ExtractConceptsResponse)
async def extract_concepts(request: ExtractConceptsRequest):
    try:
        embed_model = SentenceEmbedder(device=settings.DEVICE)
        model = TopicModeler(embed_model=embed_model, language=settings.LANGUAGE)
        concepts = await model.get_concepts(request.sentences)
        return {"concepts": concepts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))