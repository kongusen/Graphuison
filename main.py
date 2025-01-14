 # main.py
import uvicorn
from app.api import app
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True, # 自动重载
        log_level="info"
    )