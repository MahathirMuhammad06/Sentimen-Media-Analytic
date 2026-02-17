from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .crawler_routes import router as crawler_router
from .middleware import log_request
from ..database.repository import init_db, initialize_hardcoded_sources, get_session
from ..utils.logger import get_logger
from ..crawler.hybrid_manager import get_crawler_manager
from config import config
import os

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Media Analytics Backend",
    description="News crawling and sentiment analysis API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.middleware("http")(log_request)

# Include API routes
app.include_router(router)
app.include_router(crawler_router)  # Include hybrid crawler routes

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Media Analytics Backend...")
    init_db()
    logger.info("Database initialized")
    
    # Initialize hardcoded sources
    session = get_session()
    try:
        initialize_hardcoded_sources(session)
    finally:
        session.close()

    # Initialize hybrid crawler manager
    logger.info("Initializing hybrid crawler manager...")
    manager = get_crawler_manager()
    manager.initialize_crawler()
    logger.info("Hybrid crawler manager initialized")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Media Analytics Backend...")
    manager = get_crawler_manager()
    manager.shutdown()
    logger.info("Hybrid crawler manager shut down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT, reload=config.DEBUG)
