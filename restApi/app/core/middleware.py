"""
Middleware components for request/response processing.

Provides error handling, logging, and request processing middleware
for the PDF Analyzer API.
"""
import time
import traceback
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.core.exceptions import PDFAnalyzerException

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware.
    
    Catches all unhandled exceptions and converts them to standardized
    JSON responses with appropriate HTTP status codes.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and handle any exceptions.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint in the chain
            
        Returns:
            Response object (either from endpoint or error handler)
        """
        try:
            response = await call_next(request)
            return response
            
        except PDFAnalyzerException as exc:
            # Handle custom exceptions
            logger.warning(
                f"PDF Analyzer Exception: {exc.error_code} - {exc.detail}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": exc.status_code
                }
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": exc.error_code,
                        "message": exc.detail
                    }
                },
                headers=exc.headers
            )
            
        except ValueError as exc:
            # Handle validation/parsing errors
            logger.error(
                f"Value Error: {str(exc)}",
                extra={
                    "path": request.url.path,
                    "method": request.method
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(exc)
                    }
                }
            )
            
        except Exception as exc:
            # Handle unexpected exceptions
            error_id = f"{int(time.time())}"
            
            logger.error(
                f"Unhandled Exception [ID: {error_id}]: {str(exc)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error_id": error_id
                },
                exc_info=True
            )
            
            # Log full traceback in debug mode
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Traceback:\n{traceback.format_exc()}")
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "error_id": error_id
                    }
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/response logging middleware.
    
    Logs all incoming requests and outgoing responses with timing information.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log the request and response.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint in the chain
            
        Returns:
            Response from the endpoint
        """
        # Start timer
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else None,
                "query_params": dict(request.query_params)
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - {request.method} {request.url.path} ({process_time:.3f}s)",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time
            }
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class CORSHeadersMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS headers middleware.
    
    Adds additional CORS headers for better API accessibility.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add CORS headers to response.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint in the chain
            
        Returns:
            Response with CORS headers
        """
        response = await call_next(request)
        
        # Add custom CORS headers
        response.headers["X-API-Version"] = "1.0.0"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Request ID middleware.
    
    Generates and adds a unique request ID to each request for tracking.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add request ID to request and response.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint in the chain
            
        Returns:
            Response with request ID header
        """
        # Generate request ID
        request_id = f"{int(time.time() * 1000)}-{id(request)}"
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
