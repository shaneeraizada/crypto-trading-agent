# ============================================================================
# src/api/app.py
# ============================================================================
"""Main FastAPI application."""

from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.api.v1.routes import trading, portfolio, strategies, analytics, monitoring
from src.api.middleware.auth import AuthMiddleware
from src.api.middleware.rate_limiting import RateLimitMiddleware
from src.core.exceptions import TradingAgentException
from src.core.events import event_bus
from src.data.collectors.price_collector import PriceCollector
from config.settings import settings
from config.database import engine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.monitoring.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Crypto Trading Agent API")
    
    # Start event bus
    event_bus_task = None
    price_collector_task = None
    
    try:
        # Start event bus
        import asyncio
        event_bus_task = asyncio.create_task(event_bus.start())
        
        # Start price collector
        price_collector = PriceCollector()
        price_collector_task = asyncio.create_task(price_collector.start_collection())
        
        logger.info("All services started successfully")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down Crypto Trading Agent API")
        
        # Stop services
        if event_bus_task:
            await event_bus.stop()
            event_bus_task.cancel()
        
        if price_collector_task:
            price_collector_task.cancel()
        
        # Close database connections
        await engine.dispose()
        
        logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Crypto Trading Agent API",
    description="AI-powered cryptocurrency trading system with advanced analytics",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(TradingAgentException)
async def trading_agent_exception_handler(request: Request, exc: TradingAgentException):
    """Handle custom trading agent exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred"
            }
        }
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint."""
    # Check database connection, external APIs, etc.
    try:
        # Add actual health checks here
        checks = {
            "database": True,  # Check database connection
            "redis": True,     # Check Redis connection
            "apis": True,      # Check external APIs
        }
        
        all_healthy = all(checks.values())
        
        return {
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e),
                "timestamp": time.time()
            }
        )


# Include API routes
app.include_router(
    trading.router,
    prefix="/api/v1/trading",
    tags=["Trading"]
)

app.include_router(
    portfolio.router,
    prefix="/api/v1/portfolio",
    tags=["Portfolio"]
)

app.include_router(
    strategies.router,
    prefix="/api/v1/strategies",
    tags=["Strategies"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

app.include_router(
    monitoring.router,
    prefix="/api/v1/monitoring",
    tags=["Monitoring"]
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled",
        "health": "/health",
        "ready": "/ready"
    }