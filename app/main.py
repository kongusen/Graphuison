from fastapi import FastAPI
from app.api.concept_extraction import router as concept_extraction_router
from app.api.concept_extraction import router as triple_extraction_router
from app.api.fusion import router as fusion_router

app = FastAPI()

app.include_router(concept_extraction_router, prefix="/api/v1/concept")
app.include_router(triple_extraction_router, prefix="/api/v1/triple")
app.include_router(fusion_router, prefix="/api/v1/fusion")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Concept Extraction API"}