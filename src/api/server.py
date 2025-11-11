"""
FastAPI server for Burner Swarm
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from ..config.settings import Settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Evalys Burner Swarm",
    description="Disposable wallet management for Evalys ecosystem",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Evalys Burner Swarm",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {Settings.API_HOST}:{Settings.API_PORT}")
    uvicorn.run(
        app,
        host=Settings.API_HOST,
        port=Settings.API_PORT,
        reload=Settings.API_DEBUG
    )

