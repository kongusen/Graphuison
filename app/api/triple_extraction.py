from fastapi import APIRouter, HTTPException
from app.models.models import TripleExtractionInput
from app.core.triple_service import extract_triples

router = APIRouter()

@router.post("/extract/")
async def extract_triples_endpoint(input_data: TripleExtractionInput):
    try:
        result = extract_triples(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))