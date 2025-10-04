"""
Security middleware for compliance and protection.
"""

import time
import logging
import re
from typing import Callable, Set
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for request filtering and monitoring."""
    
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        
        # Security configurations
        self.blocked_user_agents = {
            'sqlmap', 'nikto', 'nmap', 'masscan', 'nessus',
            'openvas', 'w3af', 'burp', 'webscarab', 'paros'
        }
        
        self.suspicious_patterns = [
            r'(?i)(union|select|insert|update|delete|drop|create|alter)\s+',
            r'(?i)(script|javascript|vbscript|onload|onerror)',
            r'(?i)(<|%3c)(script|iframe|object|embed)',
            r'(?i)(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)',
            r'(?i)(etc\/passwd|boot\.ini|windows\/system32)',
            r'(?i)(eval\s*\(|exec\s*\(|system\s*\()'
        ]
        
        self.rate_limits = {}  # IP -> [timestamps]
        self.max_requests_per_minute = 100
        self.blocked_ips: Set[str] = set()
        
        # Security headers to add to all responses
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with security checks."""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get('user-agent', '').lower()
        
        try:
            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                logger.warning(
                    f"Blocked IP attempted access: {client_ip}",
                    extra={"custom_dimensions": {"ip": client_ip, "user_agent": user_agent}}
                )
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access forbidden"},
                    headers=self.security_headers
                )
            
            # Rate limiting check
            if not self._check_rate_limit(client_ip):
                logger.warning(
                    f"Rate limit exceeded for IP: {client_ip}",
                    extra={"custom_dimensions": {"ip": client_ip, "user_agent": user_agent}}
                )
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"},
                    headers={**self.security_headers, "Retry-After": "60"}
                )
            
            # Check for malicious user agents
            if self._is_malicious_user_agent(user_agent):
                logger.warning(
                    f"Malicious user agent detected: {user_agent}",
                    extra={"custom_dimensions": {"ip": client_ip, "user_agent": user_agent}}
                )
                self.blocked_ips.add(client_ip)
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access forbidden"},
                    headers=self.security_headers
                )
            
            # Check for suspicious patterns in request
            if await self._has_suspicious_content(request):
                logger.warning(
                    f"Suspicious request patterns detected from {client_ip}",
                    extra={
                        "custom_dimensions": {
                            "ip": client_ip,
                            "user_agent": user_agent,
                            "path": str(request.url.path),
                            "method": request.method
                        }
                    }
                )
                return JSONResponse(
                    status_code=400,
                    content={"error": "Bad request"},
                    headers=self.security_headers
                )
            
            # Validate content length
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(
                    f"Large request body from {client_ip}: {content_length} bytes",
                    extra={"custom_dimensions": {"ip": client_ip, "content_length": content_length}}
                )
                return JSONResponse(
                    status_code=413,
                    content={"error": "Request entity too large"},
                    headers=self.security_headers
                )
            
            # Process the request
            response = await call_next(request)
            
            # Add security headers to response
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            # Log successful requests for monitoring
            if hasattr(request.state, 'user_id'):
                logger.info(
                    "Authenticated request processed",
                    extra={
                        "custom_dimensions": {
                            "user_id": request.state.user_id,
                            "ip": client_ip,
                            "endpoint": f"{request.method} {request.url.path}",
                            "status_code": response.status_code
                        }
                    }
                )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Security middleware error: {str(e)}",
                extra={
                    "custom_dimensions": {
                        "ip": client_ip,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                }
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind a proxy/load balancer)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else 'unknown'
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Check if IP is within rate limits."""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Initialize or clean old entries
        if ip not in self.rate_limits:
            self.rate_limits[ip] = []
        
        # Remove old entries
        self.rate_limits[ip] = [
            timestamp for timestamp in self.rate_limits[ip]
            if timestamp > minute_ago
        ]
        
        # Check if within limits
        if len(self.rate_limits[ip]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.rate_limits[ip].append(current_time)
        return True
    
    def _is_malicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent appears to be malicious."""
        if not user_agent:
            return True  # Block empty user agents
        
        return any(
            blocked_agent in user_agent
            for blocked_agent in self.blocked_user_agents
        )
    
    async def _has_suspicious_content(self, request: Request) -> bool:
        """Check request for suspicious patterns."""
        # Check URL path
        if self._contains_suspicious_patterns(str(request.url)):
            return True
        
        # Check query parameters
        for param, value in request.query_params.items():
            if self._contains_suspicious_patterns(f"{param}={value}"):
                return True
        
        # Check headers
        for header, value in request.headers.items():
            if self._contains_suspicious_patterns(f"{header}: {value}"):
                return True
        
        # For POST/PUT requests, check body (if available)
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # Only check if content-type suggests text data
                content_type = request.headers.get('content-type', '')
                if any(ct in content_type.lower() for ct in ['json', 'form', 'text']):
                    # Note: This is a simplified check. In production, you'd want
                    # to be more careful about reading the body
                    pass
            except Exception:
                # If we can't read the body, assume it's safe
                pass
        
        return False
    
    def _contains_suspicious_patterns(self, text: str) -> bool:
        """Check if text contains suspicious patterns."""
        text_lower = text.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def get_security_stats(self) -> dict:
        """Get security statistics."""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Count recent requests per IP
        recent_requests = {}
        for ip, timestamps in self.rate_limits.items():
            recent_count = len([t for t in timestamps if t > minute_ago])
            if recent_count > 0:
                recent_requests[ip] = recent_count
        
        return {
            "blocked_ips_count": len(self.blocked_ips),
            "recent_requests_by_ip": recent_requests,
            "rate_limit_threshold": self.max_requests_per_minute,
            "security_headers": list(self.security_headers.keys())
        }
    
    def block_ip(self, ip: str, reason: str = "Manual block"):
        """Manually block an IP address."""
        self.blocked_ips.add(ip)
        logger.warning(
            f"IP {ip} has been blocked: {reason}",
            extra={"custom_dimensions": {"ip": ip, "reason": reason}}
        )
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address."""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(
                f"IP {ip} has been unblocked",
                extra={"custom_dimensions": {"ip": ip}}
            )
