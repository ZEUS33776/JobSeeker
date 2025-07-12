from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.config import settings
import os
app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    print("Port:",os.getenv("PORT"))
    return {"message": "Welcome to the Job Finder API!"}