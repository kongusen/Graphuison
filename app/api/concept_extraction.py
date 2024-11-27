from fastapi import APIRouter, HTTPException
from app.models.models import TextInput
from app.core.concept_service import extract_concepts

router = APIRouter()

@router.post("/extract/")
async def extract_concepts_endpoint(input_data: TextInput):
    try:
        result = extract_concepts(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))