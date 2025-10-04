"""
Metrics middleware for collecting application metrics.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect and expose application metrics."""
    
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        # Initialize metrics storage
        if not hasattr(app.state, 'metrics'):
            app.state.metrics = {
                'request_count': 0,
                'request_duration_total': 0.0,
                'status_codes': {},
                'endpoints': {},
                'errors': 0
            }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()
        
        # Increment request counter
        request.app.state.metrics['request_count'] += 1
        
        # Extract endpoint info
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            request.app.state.metrics['request_duration_total'] += duration
            
            # Track status codes
            status_code = response.status_code
            if status_code not in request.app.state.metrics['status_codes']:
                request.app.state.metrics['status_codes'][status_code] = 0
            request.app.state.metrics['status_codes'][status_code] += 1
            
            # Track endpoints
            if endpoint not in request.app.state.metrics['endpoints']:
                request.app.state.metrics['endpoints'][endpoint] = {
                    'count': 0,
                    'total_duration': 0.0,
                    'avg_duration': 0.0
                }
            
            endpoint_metrics = request.app.state.metrics['endpoints'][endpoint]
            endpoint_metrics['count'] += 1
            endpoint_metrics['total_duration'] += duration
            endpoint_metrics['avg_duration'] = endpoint_metrics['total_duration'] / endpoint_metrics['count']
            
            # Add metrics headers to response
            response.headers["X-Request-Duration"] = str(round(duration * 1000, 2))  # in milliseconds
            response.headers["X-Request-Count"] = str(request.app.state.metrics['request_count'])
            
            # Log metrics for Application Insights
            if duration > 2.0:  # Log slow requests
                logger.warning(
                    f"Slow request detected: {endpoint}",
                    extra={
                        "custom_dimensions": {
                            "endpoint": endpoint,
                            "duration": duration,
                            "status_code": status_code,
                            "user_agent": request.headers.get("user-agent", "unknown"),
                            "ip_address": request.client.host if request.client else "unknown"
                        }
                    }
                )
            
            return response
            
        except Exception as e:
            # Track errors
            request.app.state.metrics['errors'] += 1
            
            # Log error metrics
            duration = time.time() - start_time
            logger.error(
                f"Request error: {endpoint}",
                extra={
                    "custom_dimensions": {
                        "endpoint": endpoint,
                        "duration": duration,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "user_agent": request.headers.get("user-agent", "unknown"),
                        "ip_address": request.client.host if request.client else "unknown"
                    }
                }
            )
            
            raise


def get_metrics_summary(app) -> dict:
    """Get a summary of collected metrics."""
    if not hasattr(app.state, 'metrics'):
        return {"error": "Metrics not initialized"}
    
    metrics = app.state.metrics
    total_requests = metrics['request_count']
    
    if total_requests == 0:
        avg_duration = 0
    else:
        avg_duration = metrics['request_duration_total'] / total_requests
    
    return {
        "total_requests": total_requests,
        "total_errors": metrics['errors'],
        "error_rate": metrics['errors'] / total_requests if total_requests > 0 else 0,
        "average_response_time": round(avg_duration * 1000, 2),  # in milliseconds
        "status_code_distribution": metrics['status_codes'],
        "top_endpoints": _get_top_endpoints(metrics['endpoints']),
        "health_status": "healthy" if metrics['errors'] / max(total_requests, 1) < 0.05 else "degraded"
    }


def _get_top_endpoints(endpoints: dict, limit: int = 10) -> list:
    """Get top endpoints by request count."""
    sorted_endpoints = sorted(
        endpoints.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    
    return [
        {
            "endpoint": endpoint,
            "count": data['count'],
            "avg_duration_ms": round(data['avg_duration'] * 1000, 2)
        }
        for endpoint, data in sorted_endpoints[:limit]
    ]


def reset_metrics(app):
    """Reset all metrics counters."""
    if hasattr(app.state, 'metrics'):
        app.state.metrics = {
            'request_count': 0,
            'request_duration_total': 0.0,
            'status_codes': {},
            'endpoints': {},
            'errors': 0
        }
