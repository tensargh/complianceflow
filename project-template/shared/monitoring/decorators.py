"""
Monitoring decorators and utilities for consistent implementation.
These decorators ensure every function follows the monitoring patterns
defined in .cursorrules.
"""

import time
import logging
import functools
from typing import Any, Callable, Dict, Optional
from contextlib import asynccontextmanager
import asyncio
import traceback
from datetime import datetime

# Import Application Insights and metrics libraries
try:
    from opencensus.trace import tracer as tracer_module
    from opencensus.trace.samplers import ProbabilitySampler
    HAS_OPENCENSUS = True
except ImportError:
    HAS_OPENCENSUS = False

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Centralized metrics collection for services."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.counters: Dict[str, int] = {}
        self.timers: Dict[str, list] = {}
    
    def increment_counter(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        key = f"{self.service_name}.{metric_name}"
        if labels:
            key += f".{'.'.join(f'{k}_{v}' for k, v in labels.items())}"
        
        self.counters[key] = self.counters.get(key, 0) + 1
        
        # Log metric to Application Insights
        logger.info(
            f"Metric incremented: {metric_name}",
            extra={
                "custom_dimensions": {
                    "metric_name": metric_name,
                    "service": self.service_name,
                    "labels": labels or {},
                    "value": self.counters[key]
                }
            }
        )
    
    def start_timer(self, metric_name: str) -> 'TimerContext':
        """Start a timer for duration measurement."""
        return TimerContext(self, metric_name)
    
    def record_duration(self, metric_name: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """Record a duration metric."""
        key = f"{self.service_name}.{metric_name}"
        if key not in self.timers:
            self.timers[key] = []
        
        self.timers[key].append(duration)
        
        # Log duration to Application Insights
        logger.info(
            f"Duration recorded: {metric_name}",
            extra={
                "custom_dimensions": {
                    "metric_name": metric_name,
                    "service": self.service_name,
                    "duration_ms": duration * 1000,
                    "labels": labels or {}
                }
            }
        )


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, metrics_collector: MetricsCollector, metric_name: str):
        self.metrics_collector = metrics_collector
        self.metric_name = metric_name
        self.start_time: Optional[float] = None
        self.duration: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            self.duration = time.time() - self.start_time
            self.metrics_collector.record_duration(self.metric_name, self.duration)
    
    def stop(self):
        """Manually stop the timer."""
        if self.start_time and not self.duration:
            self.duration = time.time() - self.start_time
            self.metrics_collector.record_duration(self.metric_name, self.duration)


def trace_function(operation_name: str, service_name: Optional[str] = None):
    """
    Decorator to add comprehensive monitoring to any function.
    
    Usage:
        @trace_function("user_service.create_user")
        async def create_user(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract service name from operation name if not provided
            if service_name:
                svc_name = service_name
            else:
                svc_name = operation_name.split('.')[0] if '.' in operation_name else 'unknown'
            
            metrics = MetricsCollector(svc_name)
            timer = metrics.start_timer(f"{operation_name}.duration")
            
            # Start distributed tracing if available
            tracer = None
            span = None
            if HAS_OPENCENSUS:
                tracer = tracer_module.Tracer(sampler=ProbabilitySampler(1.0))
                span = tracer.start_span(operation_name)
            
            # Log function entry
            logger.info(
                f"Starting {operation_name}",
                extra={
                    "custom_dimensions": {
                        "operation": operation_name,
                        "service": svc_name,
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }
                }
            )
            
            try:
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Record success
                metrics.increment_counter(f"{operation_name}.success")
                
                logger.info(
                    f"Completed {operation_name} successfully",
                    extra={
                        "custom_dimensions": {
                            "operation": operation_name,
                            "service": svc_name,
                            "duration_ms": timer.duration * 1000 if timer.duration else 0
                        }
                    }
                )
                
                return result
                
            except Exception as e:
                # Record error
                metrics.increment_counter(
                    f"{operation_name}.error",
                    {"error_type": type(e).__name__}
                )
                
                logger.error(
                    f"Error in {operation_name}",
                    extra={
                        "custom_dimensions": {
                            "operation": operation_name,
                            "service": svc_name,
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "traceback": traceback.format_exc()
                        }
                    }
                )
                
                # Add error info to span
                if span:
                    span.status = f"Error: {str(e)}"
                
                raise
                
            finally:
                # Always stop timer and finish span
                timer.stop()
                if span:
                    tracer.end_span()
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar implementation for sync functions
            svc_name = service_name or operation_name.split('.')[0]
            metrics = MetricsCollector(svc_name)
            timer = metrics.start_timer(f"{operation_name}.duration")
            
            logger.info(
                f"Starting {operation_name}",
                extra={
                    "custom_dimensions": {
                        "operation": operation_name,
                        "service": svc_name,
                        "function": func.__name__
                    }
                }
            )
            
            try:
                result = func(*args, **kwargs)
                metrics.increment_counter(f"{operation_name}.success")
                
                logger.info(
                    f"Completed {operation_name} successfully",
                    extra={
                        "custom_dimensions": {
                            "operation": operation_name,
                            "service": svc_name
                        }
                    }
                )
                
                return result
                
            except Exception as e:
                metrics.increment_counter(
                    f"{operation_name}.error",
                    {"error_type": type(e).__name__}
                )
                
                logger.error(
                    f"Error in {operation_name}",
                    extra={
                        "custom_dimensions": {
                            "operation": operation_name,
                            "error": str(e),
                            "error_type": type(e).__name__
                        }
                    }
                )
                raise
                
            finally:
                timer.stop()
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def trace_method(operation_name: str):
    """
    Decorator specifically for class methods.
    
    Usage:
        class UserRepository:
            @trace_method("user_repository.get_by_id")
            async def get_by_id(self, user_id: UUID):
                pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            # Extract class name for context
            class_name = self.__class__.__name__
            service_name = getattr(self, 'service_name', class_name.lower().replace('repository', '').replace('service', ''))
            
            return await trace_function(operation_name, service_name)(func)(self, *args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            class_name = self.__class__.__name__
            service_name = getattr(self, 'service_name', class_name.lower().replace('repository', '').replace('service', ''))
            
            return trace_function(operation_name, service_name)(func)(self, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@asynccontextmanager
async def database_operation(table_name: str, operation: str, metrics_collector: MetricsCollector):
    """
    Context manager for database operations monitoring.
    
    Usage:
        async with database_operation("users", "select", metrics):
            result = await db.execute(query)
    """
    timer = metrics_collector.start_timer("database_query_duration")
    
    logger.debug(
        f"Database operation started: {operation} on {table_name}",
        extra={
            "custom_dimensions": {
                "table": table_name,
                "operation": operation,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
    
    try:
        yield
        
        metrics_collector.increment_counter(
            "database_query_success",
            {"table": table_name, "operation": operation}
        )
        
        logger.debug(
            f"Database operation completed: {operation} on {table_name}",
            extra={
                "custom_dimensions": {
                    "table": table_name,
                    "operation": operation,
                    "duration_ms": timer.duration * 1000 if timer.duration else 0
                }
            }
        )
        
    except Exception as e:
        metrics_collector.increment_counter(
            "database_query_error",
            {"table": table_name, "operation": operation, "error_type": type(e).__name__}
        )
        
        logger.error(
            f"Database operation failed: {operation} on {table_name}",
            extra={
                "custom_dimensions": {
                    "table": table_name,
                    "operation": operation,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
        )
        raise
        
    finally:
        timer.stop()


@asynccontextmanager
async def external_service_call(service_name: str, endpoint: str, metrics_collector: MetricsCollector):
    """
    Context manager for external service calls monitoring.
    
    Usage:
        async with external_service_call("declaration-service", "/api/v1/declarations", metrics):
            response = await http_client.post(url, json=data)
    """
    timer = metrics_collector.start_timer("external_service_duration")
    
    logger.info(
        f"External service call started: {service_name}{endpoint}",
        extra={
            "custom_dimensions": {
                "service": service_name,
                "endpoint": endpoint,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
    
    try:
        yield
        
        metrics_collector.increment_counter(
            "external_service_success",
            {"service": service_name, "endpoint": endpoint}
        )
        
        logger.info(
            f"External service call completed: {service_name}{endpoint}",
            extra={
                "custom_dimensions": {
                    "service": service_name,
                    "endpoint": endpoint,
                    "duration_ms": timer.duration * 1000 if timer.duration else 0
                }
            }
        )
        
    except Exception as e:
        metrics_collector.increment_counter(
            "external_service_error",
            {"service": service_name, "endpoint": endpoint, "error_type": type(e).__name__}
        )
        
        logger.error(
            f"External service call failed: {service_name}{endpoint}",
            extra={
                "custom_dimensions": {
                    "service": service_name,
                    "endpoint": endpoint,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
        )
        raise
        
    finally:
        timer.stop()


class BusinessRuleViolation(Exception):
    """Exception for business rule violations."""
    
    def __init__(self, rule: str, details: Optional[Dict[str, Any]] = None):
        self.rule = rule
        self.details = details or {}
        super().__init__(f"Business rule violated: {rule}")


def log_business_event(event_name: str, **kwargs):
    """
    Log a business event with structured data.
    
    Usage:
        log_business_event(
            "user_created",
            user_id=user.id,
            email=user.email,
            tenant_id=user.tenant_id
        )
    """
    logger.info(
        f"Business event: {event_name}",
        extra={
            "custom_dimensions": {
                "event_name": event_name,
                "timestamp": datetime.utcnow().isoformat(),
                **kwargs
            }
        }
    )


# Example usage in service implementation
class ExampleServiceWithMonitoring:
    """Example of how to use monitoring decorators in a service."""
    
    def __init__(self):
        self.service_name = "example_service"
        self.metrics = MetricsCollector(self.service_name)
    
    @trace_method("example_service.create_resource")
    async def create_resource(self, data: dict) -> dict:
        """Example method with full monitoring."""
        
        # Validate input
        if not data.get('name'):
            raise BusinessRuleViolation("Resource name is required")
        
        # Database operation
        async with database_operation("resources", "insert", self.metrics):
            # Simulated database insert
            resource_id = "new-resource-id"
        
        # External service call
        async with external_service_call("notification-service", "/api/v1/notify", self.metrics):
            # Simulated external service call
            pass
        
        # Log business event
        log_business_event(
            "resource_created",
            resource_id=resource_id,
            name=data['name']
        )
        
        return {"id": resource_id, "name": data['name']}
