from typing import TypeVar, Optional, List, Dict, Any, Generic
from datetime import datetime
import logging
from abc import ABC, abstractmethod

T = TypeVar("T", bound=Dict[str, Any])


class DatabaseError(Exception):
    """Base exception for database operations"""

    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a record is not found"""

    pass


class ValidationError(DatabaseError):
    """Raised when data validation fails"""

    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails"""

    pass


class BaseDB(ABC, Generic[T]):
    """
    Abstract base class for database operations.
    Generic type T represents the type of records being handled.
    """

    # Standard field sets that all tables should have
    BASE_FIELDS = ["id", "created_at", "updated_at", "is_active"]

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.logger = logging.getLogger(self.__class__.__name__)
        self.table_name: str = ""  # Must be set by child class

    @abstractmethod
    async def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data before database operations"""
        raise NotImplementedError

    async def _verify_connection(self) -> bool:
        """Verify the database connection is active"""
        try:
            await self.supabase.select_from_table(self.table_name, ["id"], [])
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify database connection: {str(e)}")
            raise ConnectionError("Could not establish database connection") from e

    async def _handle_db_operation(
        self, operation_name: str, operation_func, *args, **kwargs
    ) -> Any:
        """Generic error handler for database operations"""
        try:
            if not self.supabase:
                raise ConnectionError("No database connection available")
            return await operation_func(*args, **kwargs)
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Error in {operation_name}: {str(e)}", exc_info=True)
            raise DatabaseError(f"Operation {operation_name} failed") from e

    # Core CRUD Operations
    async def add(self, data: Dict[str, Any]) -> Optional[T]:
        """Create a new record"""
        if not await self._validate_data(data):
            raise ValidationError("Invalid data provided")

        async def _add_operation():
            data["created_at"] = datetime.utcnow()
            data["updated_at"] = datetime.utcnow()
            result = await self.supabase.insert_into_table(self.table_name, data)
            if not result:
                raise DatabaseError("Failed to create record")
            return result

        return await self._handle_db_operation("create", _add_operation)

    async def get_by_id(
        self, record_id: str, fields: Optional[List[str]] = None
    ) -> Optional[T]:
        """Retrieve a record by ID"""

        async def _get_operation():
            result = await self.supabase.select_from_table(
                self.table_name, fields or self.BASE_FIELDS, [("id", "eq", record_id)]
            )
            if not result:
                raise RecordNotFoundError(f"Record {record_id} not found")
            return result[0]

        return await self._handle_db_operation("get_by_id", _get_operation)

    async def update(self, record_id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update an existing record"""
        if not await self._validate_data(data):
            raise ValidationError("Invalid update data provided")

        async def _update_operation():
            data["updated_at"] = datetime.utcnow()
            result = await self.supabase.update_table(
                self.table_name, data, [("id", "eq", record_id)]
            )
            if not result:
                raise RecordNotFoundError(f"Record {record_id} not found")
            return result[0]

        return await self._handle_db_operation("update", _update_operation)

    async def delete(self, record_id: str, soft: bool = True) -> bool:
        """Delete a record (soft delete by default)"""

        async def _delete_operation():
            if soft:
                result = await self.update(record_id, {"is_active": False})
            else:
                result = await self.supabase.delete_from_table(
                    self.table_name, [("id", "eq", record_id)]
                )
            return bool(result)

        return await self._handle_db_operation("delete", _delete_operation)

    # Utility Methods
    async def exists(self, record_id: str) -> bool:
        """Check if a record exists"""
        try:
            await self.get_by_id(record_id, ["id"])
            return True
        except RecordNotFoundError:
            return False

    async def count(self, filters: Optional[List[tuple]] = None) -> int:
        """Count records matching the given filters"""

        async def _count_operation():
            result = await self.supabase.select_from_table(
                self.table_name, ["count"], filters or []
            )
            return result[0]["count"]

        return await self._handle_db_operation("count", _count_operation)

    # Batch Operations
    async def add_many(self, items: List[Dict[str, Any]]) -> List[T]:
        """Add multiple records in a single operation"""
        for item in items:
            if not await self._validate_data(item):
                raise ValidationError(f"Invalid data in batch: {item}")

        async def _add_many_operation():
            now = datetime.utcnow()
            for item in items:
                item["created_at"] = now
                item["updated_at"] = now
            result = await self.supabase.insert_into_table(self.table_name, items)
            if not result:
                raise DatabaseError("Failed to create records")
            return result

        return await self._handle_db_operation("add_many", _add_many_operation)
