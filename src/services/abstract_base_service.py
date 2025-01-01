from abc import ABC, abstractmethod
from typing import (
    Dict,
    List,
    Any,
    Optional,
    TypeVar,
    Generic,
    Callable,
    Union,
    Awaitable,
)
from datetime import datetime
import logging
import functools
from supabase import Client
import asyncio

T = TypeVar("T")


class AbstractBaseService(ABC, Generic[T]):
    def __init__(self, supabase_client: Client, table_name: str):
        self.client = supabase_client
        self.table_name = table_name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"{self.__class__.__name__}")
        # Add your logging configuration here
        return logger

    def log_operation(self, func: Callable):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            operation = func.__name__
            self.logger.debug(
                f"Starting {operation} with args: {args}, kwargs: {kwargs}"
            )

            try:
                result = func(*args, **kwargs)
                elapsed = datetime.now() - start_time
                self.logger.debug(
                    f"Completed {operation} in {elapsed.total_seconds():.2f}s"
                )
                return result
            except Exception as e:
                self.logger.error(f"Error in {operation}: {str(e)}", exc_info=True)
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            operation = func.__name__
            self.logger.debug(
                f"Starting {operation} with args: {args}, kwargs: {kwargs}"
            )

            try:
                result = await func(*args, **kwargs)
                elapsed = datetime.now() - start_time
                self.logger.debug(
                    f"Completed {operation} in {elapsed.total_seconds():.2f}s"
                )
                return result
            except Exception as e:
                self.logger.error(f"Error in {operation}: {str(e)}", exc_info=True)
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    # Sync Methods
    @abstractmethod
    def create_sync(self, data: Dict[str, Any]) -> T:
        """Create a new record synchronously"""
        pass

    @abstractmethod
    def get_by_id_sync(self, id: str) -> Optional[T]:
        """Retrieve a record by ID synchronously"""
        pass

    @abstractmethod
    def update_sync(self, id: str, data: Dict[str, Any]) -> T:
        """Update a record synchronously"""
        pass

    @abstractmethod
    def delete_sync(self, id: str) -> bool:
        """Delete a record synchronously"""
        pass

    @abstractmethod
    def list_sync(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List records with optional filters synchronously"""
        pass

    # Async Methods
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new record asynchronously"""
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Retrieve a record by ID asynchronously"""
        pass

    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> T:
        """Update a record asynchronously"""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a record asynchronously"""
        pass

    @abstractmethod
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List records with optional filters asynchronously"""
        pass
