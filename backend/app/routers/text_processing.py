# app/routers/text_processing.py
from fastapi import APIRouter, HTTPException
from backend.app.models.text_processor import TextProcessor
from backend.app.schemas.text_processing import ProcessTextRequest, ProcessTextResponse, ProcessFilesRequest
from backend.app.config import settings
from typing import List

router = APIRouter()

@router.post("/preprocess", response_model=ProcessTextResponse)
async def preprocess_text(request: ProcessTextRequest, use_llm: bool = False):
    try:
        processor = TextProcessor(language=settings.LANGUAGE)
        sentences, tokens = await processor.preprocess_text(request.text) # 移除 use_llm 参数
        return {"sentences": sentences, "tokens": tokens}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
