import asyncio
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.logger import setup_logging
import logging

# Fix for Windows asyncio subprocess issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="JobSeeker API",
    description="API for job searching and resume processing",
    version="1.0.0"
)

# CORS configuration for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Add routes at root level as well for easier access
# app.include_router(router) # This line is removed as per the new_code, as the routes are now directly included.

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {"message": "JobSeeker API is running"}

if __name__ == "__main__":
    import uvicorn
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Job Seeker Pro API server...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)