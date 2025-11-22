"""
Useful decorators for endpoint functions.

Provides reusable decorators for common endpoint patterns like
caching, validation, rate limiting, and more.
"""
import functools
import time
from typing import Callable, Any, Optional
from fastapi import Request, HTTPException, status
import logging

from app.core.exceptions import (
    BadRequestError,
    UnauthorizedError,
    PDFPasswordError,
    NotFoundError
)

logger = logging.getLogger(__name__)


def log_endpoint(func: Callable) -> Callable:
    """
    Decorator to log endpoint execution.
    
    Logs when an endpoint is called and when it completes,
    including execution time.
    
    Usage:
        @router.get("/example")
        @log_endpoint
        async def example_endpoint():
            return {"message": "Hello"}
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        func_name = func.__name__
        start_time = time.time()
        
        logger.debug(f"Executing endpoint: {func_name}")
        
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"Endpoint {func_name} completed in {elapsed:.3f}s")
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Endpoint {func_name} failed after {elapsed:.3f}s: {str(e)}")
            raise
            
    return wrapper


def require_password(from_query: bool = False, from_header: bool = True):
    """
    Decorator to enforce PDF password requirement.
    
    Args:
        from_query: Allow password from query parameter 'password'
        from_header: Allow password from header 'X-PDF-Password'
    
    Usage:
        @router.post("/analyze")
        @require_password(from_query=True, from_header=True)
        async def analyze_pdf(request: Request, password: str = None):
            # password will be extracted from query/header if not provided
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Find request object in args/kwargs
            request: Optional[Request] = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                request = kwargs.get('request')
            
            if not request:
                raise PDFPasswordError("Request object not found")
            
            # Check if password is already provided
            password = kwargs.get('password')
            
            if not password:
                # Try to get from header
                if from_header:
                    password = request.headers.get('X-PDF-Password')
                
                # Try to get from query
                if not password and from_query:
                    password = request.query_params.get('password')
                
                # Inject password into kwargs
                if password:
                    kwargs['password'] = password
            
            # Validate password exists
            if not kwargs.get('password'):
                raise PDFPasswordError(
                    "PDF password required. Provide via 'X-PDF-Password' header or 'password' query parameter."
                )
            
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator


def validate_filename_format(param_name: str = "filename"):
    """
    Decorator to validate PDF filename format.
    
    Ensures the filename follows the expected format:
    Extracto_{id}_{YYYYMM}_{tipo}_{numero}.pdf
    
    Args:
        param_name: Name of the parameter containing the filename
    
    Usage:
        @router.get("/pdf/{filename}")
        @validate_filename_format(param_name="filename")
        async def get_pdf(filename: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            filename = kwargs.get(param_name)
            
            if not filename:
                raise BadRequestError(f"Missing required parameter: {param_name}")
            
            # Basic validation
            if not filename.startswith("Extracto_") or not filename.endswith(".pdf"):
                from app.core.exceptions import InvalidFilenameError
                raise InvalidFilenameError(filename)
            
            # Validate format: Extracto_{id}_{YYYYMM}_{tipo}_{numero}.pdf
            parts = filename.replace(".pdf", "").split("_")
            
            if len(parts) < 5:
                from app.core.exceptions import InvalidFilenameError
                raise InvalidFilenameError(filename)
            
            # Validate date format (YYYYMM)
            date_part = parts[2]
            if len(date_part) != 6 or not date_part.isdigit():
                from app.core.exceptions import InvalidFilenameError
                raise InvalidFilenameError(filename)
            
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator


def cache_response(ttl_seconds: int = 300):
    """
    Decorator to cache endpoint responses.
    
    Args:
        ttl_seconds: Time to live for cached responses in seconds
    
    Usage:
        @router.get("/expensive-operation")
        @cache_response(ttl_seconds=600)
        async def expensive_operation():
            # This response will be cached for 10 minutes
            ...
    
    Note: This is a simple in-memory cache. For production,
    consider using Redis or similar.
    """
    cache: dict[str, tuple[Any, float]] = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
                else:
                    # Cache expired
                    del cache[cache_key]
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache[cache_key] = (result, time.time())
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
            
        return wrapper
    return decorator


def handle_not_found(resource_name: str = "Resource"):
    """
    Decorator to convert None results to 404 errors.
    
    Args:
        resource_name: Name of the resource for error message
    
    Usage:
        @router.get("/pdf/{filename}")
        @handle_not_found(resource_name="PDF file")
        async def get_pdf(filename: str):
            # If this returns None, a 404 will be raised
            return find_pdf(filename)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            result = await func(*args, **kwargs)
            
            if result is None:
                raise NotFoundError(f"{resource_name} not found")
            
            return result
            
        return wrapper
    return decorator


def require_fields(*field_names: str):
    """
    Decorator to validate required fields in request body.
    
    Args:
        *field_names: Names of required fields
    
    Usage:
        @router.post("/create")
        @require_fields("name", "email")
        async def create_user(data: dict):
            # Ensures 'name' and 'email' are present in data
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Find dict-like object in kwargs (usually 'data' or 'body')
            data = None
            for key in ['data', 'body', 'request_data']:
                if key in kwargs:
                    data = kwargs[key]
                    break
            
            if data is None:
                raise BadRequestError("Request data not found")
            
            # Check required fields
            missing_fields = [
                field for field in field_names 
                if field not in data or data[field] is None
            ]
            
            if missing_fields:
                raise BadRequestError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator


def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure and log execution time.
    
    Usage:
        @router.get("/slow-operation")
        @timing_decorator
        async def slow_operation():
            ...
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        
        logger.info(f"{func.__name__} took {elapsed:.3f}s to execute")
        
        return result
        
    return wrapper
