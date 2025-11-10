from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .routers import videos
from .utils.logging_setup import logger

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

app = FastAPI(
    title="Content Gen Backend",
    description="AI-powered content generation with Sora video API",
    version="1.0.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Restricted for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3333", "http://localhost:3334", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specific methods only
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],  # Specific headers only
)

# Include routers
app.include_router(videos.router)

logger.info("FastAPI application initialized")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "content-gen-backend", "version": "1.0.0"}


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Application starting up...")
    logger.info("Video API endpoints available at /api/v1/videos")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Application shutting down...")
