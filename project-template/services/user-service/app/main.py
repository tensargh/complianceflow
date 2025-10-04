"""
User Service - Compliance Flow Platform
Main FastAPI application entry point with comprehensive monitoring and observability
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import time
import os
from typing import Dict, Any

# Application Insights and OpenTelemetry
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace import config_integration
from opencensus.ext.fastapi.fastapi_middleware import FastAPIMiddleware

from app.core.config import settings
from app.core.database import init_db, get_db
from app.core.logging import setup_logging
from app.api.routes import auth, users, business_units
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.metrics import MetricsMiddleware
from app.middleware.security import SecurityMiddleware

# Setup logging and monitoring
setup_logging()

# Configure OpenCensus integrations for distributed tracing
config_integration.trace_integrations(['sqlalchemy', 'requests', 'httpx', 'postgresql'])

# Application start time for metrics
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with monitoring."""
    # Startup
    logging.info("Starting User Service...")
    try:
        await init_db()
        logging.info("Database initialized successfully")
        
        # Log service startup to Application Insights
        logger = logging.getLogger(__name__)
        logger.info(
            "User Service started successfully",
            extra={
                "custom_dimensions": {
                    "service": "user-service",
                    "version": "1.0.0",
                    "environment": settings.environment,
                    "startup_time": time.time() - START_TIME
                }
            }
        )
    except Exception as e:
        logging.error(f"Failed to start User Service: {e}")
        raise
    
    yield
    
    # Shutdown
    logging.info("Shutting down User Service...")


# Create FastAPI application with enhanced configuration
app = FastAPI(
    title="Compliance Flow - User Service",
    description="Identity and Access Management Service for Compliance Flow Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "prod" else None,
    redoc_url="/redoc" if settings.environment != "prod" else None,
    openapi_url="/openapi.json" if settings.environment != "prod" else None,
)

# Store start time in app state
app.state.start_time = START_TIME

# Add Application Insights middleware for distributed tracing
if hasattr(settings, 'APPLICATIONINSIGHTS_CONNECTION_STRING') and settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
    app.add_middleware(
        FastAPIMiddleware,
        exporter=AzureExporter(
            connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING
        ),
        sampler=ProbabilitySampler(rate=getattr(settings, 'MONITORING_SAMPLING_RATE', 1.0))
    )

# Add security middleware (before CORS)
app.add_middleware(SecurityMiddleware)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'allowed_origins', ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for production security
if hasattr(settings, 'allowed_hosts') and settings.allowed_hosts:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Request ID and error handling middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(business_units.router, prefix="/api/v1/business-units", tags=["Business Units"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "service": "user-service",
        "version": "1.0.0",
        "status": "healthy",
        "description": "Identity and Access Management for Compliance Flow",
        "timestamp": time.time(),
        "environment": settings.environment
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0",
        "timestamp": time.time(),
        "environment": settings.environment,
        "uptime_seconds": time.time() - START_TIME
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness check - verifies database connectivity and dependencies."""
    try:
        # Check database connection
        async for db in get_db():
            result = await db.execute("SELECT 1")
            if not result:
                raise Exception("Database query failed")
            break
        
        # Add other dependency checks here (Redis, Kafka, etc.)
        
        return {
            "status": "ready",
            "service": "user-service",
            "version": "1.0.0",
            "timestamp": time.time(),
            "dependencies": {
                "database": "connected",
                # Add other dependencies status
            }
        }
    except Exception as e:
        logging.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "service": "user-service",
                "error": str(e),
                "timestamp": time.time()
            }
        )


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Liveness check - basic service responsiveness."""
    return {
        "status": "alive",
        "service": "user-service",
        "version": "1.0.0",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - START_TIME
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    uptime = time.time() - START_TIME
    
    # Basic metrics - in production this would use prometheus_client
    metrics_data = {
        "service_info": {
            "name": "user_service",
            "version": "1.0.0",
            "environment": settings.environment
        },
        "uptime_seconds": uptime,
        "start_time": START_TIME,
        "current_time": time.time(),
        # Add more metrics as needed
        "memory_usage": _get_memory_usage(),
        "request_count": getattr(app.state, 'request_count', 0)
    }
    
    return metrics_data


def _get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage information."""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            "rss_bytes": memory_info.rss,
            "vms_bytes": memory_info.vms,
            "percent": process.memory_percent()
        }
    except ImportError:
        return {"error": "psutil not available"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "dev"
    )
