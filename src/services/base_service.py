from typing import Optional, Any, Dict, List, Callable
from datetime import datetime
import logging
import functools
import asyncio
from postgrest import AsyncFilterRequestBuilder, FilterRequestBuilder
from postgrest.exceptions import APIError

class ServiceError(Exception):
    """Base exception for service errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class NotFoundError(ServiceError):
    """Raised when a resource is not found"""
    pass

class DuplicateError(ServiceError):
    """Raised when attempting to create a duplicate resource"""
    pass

class ValidationError(ServiceError):
    """Raised when data validation fails"""
    pass

class DatabaseError(ServiceError):
    """Raised when a database operation fails"""
    pass

class AuthenticationError(ServiceError):
    """Raised when authentication fails"""
    pass

class BaseService:
    # Error codes from Postgres that we want to handle specifically
    ERROR_CODES = {
        "23505": DuplicateError,  # unique_violation
        "23503": ValidationError, # foreign_key_violation
        "23502": ValidationError, # not_null_violation
        "22P02": ValidationError, # invalid_text_representation
        "42P01": DatabaseError,   # undefined_table
    }

    def __init__(
        self,
        supabase_client,
        table_name: str,
        logger_name: Optional[str] = None,
        log_level: int = logging.INFO
    ):
        self.logger_name = logger_name or f"{self.__class__.__name__}"
        self.logger = self._setup_logger(log_level)
        self.table_name = table_name
        self.client = supabase_client
        
        self.logger.info(f"Initialized {self.logger_name} for table {self.table_name}")

    def _setup_logger(self, log_level: int) -> logging.Logger:
        # ... same as before ...

    def handle_error(self, error: Exception, operation: str) -> Exception:
        """Convert database errors to service errors"""
        if isinstance(error, APIError):
            # Handle Postgrest API errors
            if error.code == "PGRST116":
                return NotFoundError(f"Resource not found during {operation}")
            
            # Handle Postgres errors
            pg_error = error.details
            if pg_error and "code" in pg_error:
                error_class = self.ERROR_CODES.get(pg_error["code"], DatabaseError)
                return error_class(
                    f"Database error during {operation}: {pg_error.get('message')}",
                    original_error=error
                )
        
        if isinstance(error, ServiceError):
            return error
            
        return DatabaseError(f"Unexpected error during {operation}", original_error=error)

    def log_operation(self, func: Callable) -> Callable:
        """Enhanced decorator with error handling"""
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            operation = func.__name__
            self.logger.debug(f"Starting async {operation} with args: {args}, kwargs: {kwargs}")
            
            try:
                result = await func(*args, **kwargs)
                elapsed = datetime.now() - start_time
                self.logger.debug(f"Completed async {operation} in {elapsed.total_seconds():.2f}s")
                return result
            except Exception as e:
                error = self.handle_error(e, operation)
                self.logger.error(
                    f"Error in async {operation}: {str(error)}", 
                    exc_info=True
                )
                raise error

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            operation = func.__name__
            self.logger.debug(f"Starting sync {operation} with args: {args}, kwargs: {kwargs}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = datetime.now() - start_time
                self.logger.debug(f"Completed sync {operation} in {elapsed.total_seconds():.2f}s")
                return result
            except Exception as e:
                error = self.handle_error(e, operation)
                self.logger.error(
                    f"Error in sync {operation}: {str(error)}", 
                    exc_info=True
                )
                raise error

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    # Database operations with error handling
    @log_operation
    async def async_get_by_id(self, id: str) -> Dict[str, Any]:
        """Get a single record by ID asynchronously"""
        result = await self.client.from_(self.table_name).select("*").eq("id", id).single()
        if not result:
            raise NotFoundError(f"No {self.table_name} found with id {id}")
        return result

    # ... other async and sync methods as before ...

    async def safe_async_get(self, id: str) -> Optional[Dict[str, Any]]:
        """Safely get a record, returning None if not found"""
        try:
            return await self.async_get_by_id(id)
        except NotFoundError:
            return None
        except Exception as e:
            self.logger.warning(f"Error fetching {self.table_name} {id}: {str(e)}")
            return None 