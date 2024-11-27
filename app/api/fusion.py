from fastapi import APIRouter, HTTPException
from app.models.models import FusionInput
from app.core.fusion_service import fuse_triples

router = APIRouter()

@router.post("/fuse/")
async def fuse_triples_endpoint(input_data: FusionInput):
    try:
        result = fuse_triples(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))