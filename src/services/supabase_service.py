from supabase import AsyncClient
import asyncio
from pathlib import Path
import sys

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.base_logging import Logger, log_method
from src.services.exceptions import (
    SupabaseConnectionError,
    SupabaseQueryError,
    SupabaseAuthenticationError,
    SupabaseAuthorizationError,
    SupabaseError,
    SupabaseStorageError,
    map_storage_error,
)
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Callable, List, Dict, Tuple, Union
from tenacity import retry, stop_after_attempt, wait_exponential
from supabase.lib.client_options import ClientOptions


def make_sync(async_func):
    """Decorator to convert async methods to sync methods."""

    @wraps(async_func)
    def sync_wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If we're in a running event loop, use a thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    lambda: asyncio.run(async_func(*args, **kwargs))
                )
                return future.result()
        else:
            # If no loop is running, we can just run it directly
            return loop.run_until_complete(async_func(*args, **kwargs))

    return sync_wrapper


class SupabaseService:
    """Service class for interacting with Supabase.

    Provides methods for database operations, authentication, storage,
    and realtime subscriptions.

    Attributes:
        url (str): Supabase project URL
        api_key (str): Supabase API key
    """

    DEFAULT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    CHUNK_SIZE = 1000  # for bulk operations
    STORAGE_UPLOAD_LIMIT = 50 * 1024 * 1024  # 50MB
    ALLOWED_OPERATORS = [
        "eq",  # equals
        "neq",  # not equals
        "gt",  # greater than
        "gte",  # greater than or equal
        "lt",  # less than
        "lte",  # less than or equal
        "like",  # LIKE operator
        "ilike",  # case insensitive LIKE
        "is",  # IS operator (for null)
        "in",  # IN operator
        "contains",  # contains for arrays/json
        "contained_by",  # contained by for arrays/json
        "text_search",  # full text search
    ]

    def __init__(self, url: str, api_key: str):
        if not url or not api_key:
            raise SupabaseError("URL and API key are required")
        self.url = url
        self.api_key = api_key
        self._logger = Logger(self.__class__.__name__)
        self._init_client()

    @log_method()
    def _init_client(self) -> None:
        """Initialize the Supabase async client.

        Raises:
            SupabaseConnectionError: If client initialization fails
        """
        try:
            options = ClientOptions(
                schema="public",
                headers={"x-my-custom-header": "my-app-name"},
                persist_session=True,
                auto_refresh_token=True,
                postgrest_client_timeout=self.DEFAULT_TIMEOUT,
            )
            self._supabase = AsyncClient(self.url, self.api_key, options=options)
        except Exception as e:
            raise SupabaseConnectionError(
                "Failed to initialize client", original_error=e
            )

    @property
    def supabase(self) -> AsyncClient:
        """Get the Supabase client instance.

        Returns:
            AsyncClient: The initialized Supabase client

        Raises:
            SupabaseConnectionError: If client is not properly initialized
        """
        if not hasattr(self, "_supabase") or not isinstance(
            self._supabase, AsyncClient
        ):
            self._logger.error("Supabase client not properly initialized")
            raise SupabaseConnectionError("Supabase client not properly initialized")
        return self._supabase

    @log_method()
    async def select_from_table(
        self,
        table_name: str,
        fields: Union[dict, str],
        where_filters: Optional[List[Tuple[str, str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Query data from a Supabase table with optional filters.

        Args:
            table_name: Name of the table to query
            fields: Dictionary of fields to select or "*" for all fields
            where_filters: Optional list of filters in format [(column, operator, value)]

        Returns:
            list | None: List of matching records or None if no matches/error
        """
        if not isinstance(table_name, str) or not table_name.strip():
            raise ValueError("Table name must be a non-empty string")

        if not isinstance(fields, (dict, str)):
            raise ValueError("Fields must be either a dictionary or string")

        if where_filters and not all(
            isinstance(f, tuple) and len(f) == 3 for f in where_filters
        ):
            raise ValueError("Invalid where_filters format")

        try:
            if fields == "*":
                query = self.supabase.table(table_name).select("*")
            else:
                query = self.supabase.table(table_name).select(",".join(fields))

                if where_filters:
                    for filter in where_filters:
                        column, operator, value = filter
                        if operator == "eq":
                            query = query.eq(column, value)
                        elif operator == "neq":
                            query = query.neq(column, value)
                        elif operator == "lt":
                            query = query.lt(column, value)
                        elif operator == "lte":
                            query = query.lte(column, value)
                        elif operator == "gt":
                            query = query.gt(column, value)
                        elif operator == "gte":
                            query = query.gte(column, value)
                        elif operator == "like":
                            query = query.like(column, value)
                        elif operator == "ilike":
                            query = query.ilike(column, value)
                        elif operator == "is":
                            query = query.is_(column, value)
                        elif operator == "in":
                            query = query.in_(column, value)
                        elif operator == "contains":
                            query = query.contains(column, value)
                        elif operator == "contained_by":
                            query = query.contained_by(column, value)
                        elif operator == "text_search":
                            query = query.text_search(column, value)
                        else:
                            raise ValueError(f"Unsupported operator: {operator}")

            response = await query.execute()
            if not response or not hasattr(response, "data"):
                return None
            return response.data
        except Exception as e:
            raise SupabaseQueryError(
                f"Failed to select from table {table_name}", original_error=e
            )

    @log_method()
    async def update_table(
        self, table_name: str, update_fields: dict, where_filters: list
    ) -> dict | None:
        """Update records in a table matching the given filters.

        Args:
            table_name: Name of the table to update
            update_fields: Dictionary of fields and values to update
            where_filters: List of filters in format [(column, operator, value)]

        Returns:
            dict | None: First updated record or None if no updates/error
        """
        if not table_name:
            raise SupabaseError("Table name is required")

        try:
            serialized_fields = self._serialize_data(update_fields)
            query = self.supabase.table(table_name).update(serialized_fields)

            if where_filters:
                self._logger.debug(f"Applying filters: {where_filters}")
                for filter in where_filters:
                    column, operator, value = filter
                    if operator == "eq":
                        query = query.eq(column, value)
                    elif operator == "neq":
                        query = query.neq(column, value)
                    elif operator == "lt":
                        query = query.lt(column, value)
                    elif operator == "lte":
                        query = query.lte(column, value)
                    elif operator == "gt":
                        query = query.gt(column, value)
                    elif operator == "gte":
                        query = query.gte(column, value)
                    elif operator == "like":
                        query = query.like(column, value)
                    elif operator == "ilike":
                        query = query.ilike(column, value)
                    elif operator == "is":
                        query = query.is_(column, value)
                    elif operator == "in":
                        query = query.in_(column, value)
                    elif operator == "contains":
                        query = query.contains(column, value)
                    elif operator == "contained_by":
                        query = query.contained_by(column, value)
                    elif operator == "text_search":
                        query = query.text_search(column, value)
                    else:
                        self._logger.error(f"Unsupported operator: {operator}")
                        raise ValueError(f"Unsupported operator: {operator}")

            response = await query.execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            raise SupabaseQueryError("Failed to update table", original_error=e)

    @log_method()
    async def insert_into_table(
        self, table_name: str, insert_fields: dict, upsert: bool = False
    ) -> dict | None:
        """Insert new record(s) into a table.

        Args:
            table_name: Name of the table for insertion
            insert_fields: Dictionary of fields and values to insert
            upsert: If True, update existing record instead of failing

        Returns:
            dict | None: Inserted record or None if insertion failed
        """
        if not table_name:
            raise SupabaseError("Table name is required")

        try:
            query = self.supabase.table(table_name)
            if upsert:
                response = await query.upsert(insert_fields).execute()
            else:
                response = await query.insert(insert_fields).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            raise SupabaseQueryError("Failed to insert into table", original_error=e)

    @log_method()
    async def delete_from_table(self, table_name: str, where_filters: list) -> bool:
        """Delete records from a table matching the given filters.

        Args:
            table_name: Name of the table to delete from
            where_filters: List of filters in format [(column, operator, value)]

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not table_name:
            raise SupabaseError("Table name is required")

        try:
            query = self.supabase.table(table_name)
            for filter in where_filters:
                column, operator, value = filter
                if operator == "eq":
                    query = query.eq(column, value)
                # ... [existing operator conditions remain unchanged] ...
                else:
                    raise ValueError(f"Unsupported operator: {operator}")

            response = await query.delete().execute()
            return bool(response and hasattr(response, "data"))
        except Exception as e:
            raise SupabaseQueryError("Failed to delete from table", original_error=e)

    @log_method()
    async def login(self, email: str, password: str) -> bool:
        """Login to Supabase with email and password."""
        if not email or not password:
            raise SupabaseError("Email and password are required")

        try:
            response = await self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if not response or not response.user:
                raise SupabaseAuthenticationError("Login failed - invalid credentials")
            self.session = response.session
            return True
        except Exception as e:
            raise SupabaseAuthenticationError("Authentication failed", original_error=e)

    @log_method()
    async def logout(self) -> bool:
        """Logout current user.

        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            await self.supabase.auth.sign_out()
            self.session = None
            return True
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to logout", original_error=e)

    @log_method()
    async def reset_password(self, email: str) -> bool:
        """Request password reset for email.

        Args:
            email: Email address for password reset

        Returns:
            bool: True if reset email sent successfully, False otherwise
        """
        try:
            await self.supabase.auth.reset_password_for_email(email)
            return True
        except Exception as e:
            raise SupabaseAuthenticationError(
                "Failed to reset password", original_error=e
            )

    @log_method()
    async def signup(self, email: str, password: str) -> tuple[bool, str | None]:
        """Sign up new user with email and password.

        Args:
            email: New user's email address
            password: New user's password

        Returns:
            tuple: (success: bool, error_message: str | None)
        """
        try:
            await self.supabase.auth.sign_up({"email": email, "password": password})
            return True, None
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to signup", original_error=e)

    @log_method()
    def _serialize_data(self, data: dict) -> dict:
        """Serialize data for Supabase by converting Python types to JSON-compatible types.

        Args:
            data: Dictionary of data to serialize

        Returns:
            dict: Serialized data with JSON-compatible types
        """
        serialized = {}
        for key, value in data.items():
            if isinstance(value, bool):
                serialized[key] = str(value).lower()  # Convert bool to 'true'/'false'
            else:
                serialized[key] = value
        return serialized

    @log_method()
    async def get_user(self):
        """Get the currently logged in user's details.

        Returns:
            dict | None: User details if logged in, None otherwise
        """
        try:
            user = await self.supabase.auth.get_user()
            if user and hasattr(user, "user"):
                return user.user
            return None
        except Exception:
            return None

    @log_method()
    async def set_current_domain(self, domain_id: Optional[str]) -> None:
        """Set the current domain for subsequent Supabase operations.

        Args:
            domain_id: ID of the domain to set as current, or None to clear

        Raises:
            Exception: If the server returns an invalid response
        """
        try:
            response = await self.supabase.rpc(
                "set_current_domain", {"domain_id": domain_id}
            ).execute()

            if not hasattr(response, "data"):
                raise Exception("Invalid response from server")
        except Exception as e:
            raise SupabaseAuthorizationError(
                "Failed to set current domain", original_error=e
            )

    # Storage Methods
    @log_method()
    async def upload_file(
        self, bucket: str, file_path: str, file_data: bytes, content_type: str = None
    ) -> str:
        """Upload a file to Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_path: Path where file will be stored
            file_data: Binary file data
            content_type: MIME type of the file

        Returns:
            str: Public URL of the uploaded file

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageQuotaError: If storage quota is exceeded
            SupabaseStorageValidationError: If file validation fails
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_data:
            raise ValueError("File data cannot be empty")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")

        try:
            response = await self.supabase.storage.from_(bucket).upload(
                file_path,
                file_data,
                {"content-type": content_type} if content_type else None,
            )
            if not response or "Key" not in response:
                raise SupabaseStorageError("Invalid response from storage upload")
            return response["Key"]
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to upload file", original_error=e)

    @log_method()
    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """Download a file from Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_path: Path to the file

        Returns:
            bytes: File data

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If file not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")

        try:
            response = await self.supabase.storage.from_(bucket).download(file_path)
            if not response:
                raise SupabaseStorageError("No data received from storage download")
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to download file", original_error=e)

    @log_method()
    async def delete_file(self, bucket: str, file_paths: list[str]) -> bool:
        """Delete files from Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_paths: List of file paths to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If any file not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_paths or not isinstance(file_paths, list):
            raise ValueError("File paths must be a non-empty list")
        if not all(isinstance(path, str) for path in file_paths):
            raise ValueError("All file paths must be strings")

        try:
            await self.supabase.storage.from_(bucket).remove(file_paths)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to delete files", original_error=e)

    @log_method()
    async def list_files(self, bucket: str, path: str = "") -> list[dict]:
        """List files in a storage bucket.

        Args:
            bucket: Storage bucket name
            path: Optional path prefix to filter by

        Returns:
            list[dict]: List of file metadata

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not isinstance(path, str):
            raise ValueError("Path must be a string")

        try:
            response = await self.supabase.storage.from_(bucket).list(path)
            if response is None:
                return []
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to list files", original_error=e)

    # Enhanced Authentication Methods
    @log_method()
    async def login_with_provider(
        self, provider: str, redirect_url: str = None
    ) -> Dict[str, Any]:
        """Login with OAuth provider (Google, GitHub, etc.).

        Args:
            provider: OAuth provider name
            redirect_url: URL to redirect after authentication

        Returns:
            dict: Provider session information
        """
        try:
            response = await self.supabase.auth.sign_in_with_oauth(
                {
                    "provider": provider,
                    "options": {"redirect_to": redirect_url} if redirect_url else None,
                }
            )
            return response
        except Exception as e:
            raise SupabaseAuthenticationError(
                f"Failed to login with {provider}", original_error=e
            )

    @log_method()
    async def refresh_session(self) -> dict:
        """Refresh the current session token.

        Returns:
            dict: New session data
        """
        try:
            response = await self.supabase.auth.refresh_session()
            return response
        except Exception as e:
            raise SupabaseAuthenticationError(
                "Failed to refresh session", original_error=e
            )

    @log_method()
    async def update_user(self, attributes: dict) -> dict:
        """Update the current user's attributes.

        Args:
            attributes: Dictionary of user attributes to update

        Returns:
            dict: Updated user data
        """
        try:
            response = await self.supabase.auth.update_user(attributes)
            return response.user
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to update user", original_error=e)

    # Role-Based Access Control Methods
    @log_method()
    async def get_user_roles(
        self, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns user roles with additional metadata
        Example return: [{"role": "admin", "assigned_at": "2024-01-01"}]
        """
        try:
            response = await self.supabase.rpc(
                "get_user_roles", {"p_user_id": user_id}
            ).execute()
            return response.data
        except Exception as e:
            raise SupabaseAuthorizationError(
                "Failed to get user roles", original_error=e
            )

    @log_method()
    async def check_permission(self, permission: str) -> bool:
        """Check if current user has specific permission.

        Args:
            permission: Permission to check

        Returns:
            bool: True if user has permission
        """
        try:
            response = await self.supabase.rpc(
                "check_permission", {"p_permission": permission}
            ).execute()
            return response.data
        except Exception as e:
            raise SupabaseAuthorizationError(
                "Failed to check permission", original_error=e
            )

    # Realtime Subscription Methods
    @log_method()
    async def subscribe_to_table(
        self,
        table_name: str,
        callback: Callable[[Dict[str, Any]], None],
        event: str = "*",
        filter_str: Optional[str] = None,
    ) -> Any:
        """Subscribe to real-time changes on a table.

        Args:
            table_name: Name of table to subscribe to
            callback: Function to call when changes occur
            event: Event type to listen for ("INSERT", "UPDATE", "DELETE", or "*")
            filter_str: Optional filter string
        """
        try:
            channel = self.supabase.channel("db-changes")
            channel.on(
                "postgres_changes",
                event=event,
                schema="public",
                table=table_name,
                filter=filter_str,
                callback=callback,
            )
            await channel.subscribe()
            return channel
        except Exception as e:
            raise SupabaseError("Failed to create subscription", original_error=e)

    # Storage Bucket Management Methods
    @log_method()
    async def create_bucket(self, bucket_name: str, is_public: bool = False) -> dict:
        """Create a new storage bucket.

        Args:
            bucket_name: Name of the bucket to create
            is_public: Whether the bucket should be public

        Returns:
            dict: Created bucket information

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageValidationError: If bucket name is invalid
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")
        if not isinstance(is_public, bool):
            raise ValueError("is_public must be a boolean")

        try:
            response = await self.supabase.storage.create_bucket(
                bucket_name, {"public": is_public}
            )
            if not response:
                raise SupabaseStorageError("Invalid response from bucket creation")
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to create bucket", original_error=e)

    @log_method()
    async def get_bucket(self, bucket_name: str) -> dict:
        """Get bucket information.

        Args:
            bucket_name: Name of the bucket

        Returns:
            dict: Bucket information
        """
        try:
            return await self.supabase.storage.get_bucket(bucket_name)
        except Exception as e:
            raise SupabaseError("Failed to get bucket", original_error=e)

    @log_method()
    async def list_buckets(self) -> list[dict]:
        """List all storage buckets.

        Returns:
            list[dict]: List of bucket information
        """
        try:
            return await self.supabase.storage.list_buckets()
        except Exception as e:
            raise SupabaseError("Failed to list buckets", original_error=e)

    @log_method()
    async def delete_bucket(self, bucket_name: str) -> bool:
        """Delete a storage bucket.

        Args:
            bucket_name: Name of the bucket to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")

        try:
            await self.supabase.storage.delete_bucket(bucket_name)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to delete bucket", original_error=e)

    @log_method()
    async def empty_bucket(self, bucket_name: str) -> bool:
        """Empty a storage bucket.

        Args:
            bucket_name: Name of the bucket to empty

        Returns:
            bool: True if operation was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")

        try:
            await self.supabase.storage.empty_bucket(bucket_name)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to empty bucket", original_error=e)

    # RPC Methods
    @log_method()
    async def rpc(self, function_name: str, params: dict = None) -> Any:
        """Call a Postgres function via RPC.

        Args:
            function_name: Name of the function to call
            params: Optional parameters for the function

        Returns:
            Any: Function result
        """
        try:
            response = await self.supabase.rpc(function_name, params or {}).execute()
            return response.data
        except Exception as e:
            raise SupabaseError(f"RPC call to {function_name} failed", original_error=e)

    # Add sync versions for new methods

    # Enhanced Authentication Methods
    @log_method()
    async def update_password(self, new_password: str) -> bool:
        """Update password for the currently logged-in user.

        Args:
            new_password: The new password to set

        Returns:
            bool: True if password was updated successfully
        """
        try:
            await self.supabase.auth.update_user({"password": new_password})
            return True
        except Exception as e:
            raise SupabaseAuthenticationError(
                "Failed to update password", original_error=e
            )

    @log_method()
    async def verify_otp(self, email: str, token: str) -> bool:
        """Verify one-time password token.

        Args:
            email: User's email address
            token: OTP token to verify

        Returns:
            bool: True if verification successful
        """
        try:
            await self.supabase.auth.verify_otp(
                {"email": email, "token": token, "type": "email"}
            )
            return True
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to verify OTP", original_error=e)

    @log_method()
    async def set_session(self, access_token: str, refresh_token: str) -> bool:
        """Manually set the session tokens.

        Args:
            access_token: JWT access token
            refresh_token: Refresh token

        Returns:
            bool: True if session was set successfully
        """
        try:
            await self.supabase.auth.set_session(access_token, refresh_token)
            return True
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to set session", original_error=e)

    # Advanced Query Methods
    @log_method()
    async def select_with_join(
        self,
        table_name: str,
        foreign_table: str,
        fields: list[str],
        join_column: str,
        foreign_key: str,
        where_filters: list = None,
    ) -> list:
        """Select data with a JOIN operation.

        Args:
            table_name: Primary table name
            foreign_table: Table to join with
            fields: List of fields to select (format: ["table1.field1", "table2.field2"])
            join_column: Column from primary table for joining
            foreign_key: Column from foreign table for joining
            where_filters: Optional filters in format [(column, operator, value)]

        Returns:
            list: Query results with joined data

        Raises:
            SupabaseQueryError: If the join operation fails
            ValueError: If invalid join parameters are provided
        """
        try:
            query = (
                self.supabase.from_(table_name)
                .select(",".join(fields))
                .join(foreign_table, f"{join_column}=eq.{foreign_key}")
            )

            if where_filters:
                for filter in where_filters:
                    column, operator, value = filter
                    query = self._apply_filter(query, column, operator, value)

            response = await query.execute()
            return response.data
        except Exception as e:
            raise SupabaseQueryError("Failed to execute join query", original_error=e)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    @log_method()
    async def cleanup(self):
        """Cleanup resources when service is no longer needed."""
        try:
            await self.supabase.auth.sign_out()
            # Add any other cleanup needed
        except Exception as e:
            self._logger.error("Error during cleanup", error=e)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    def _is_token_expiring_soon(self, token: str, threshold_minutes: int = 5) -> bool:
        # Add JWT expiration checking logic
        pass

    async def _ensure_connected(self):
        """Ensure connection is available before operations."""
        if not await self.check_connection():
            await self._init_client()  # Reinitialize if needed

    async def create_search_index(self, table_name: str, column_name: str) -> bool:
        """
        Create a GIN index for full-text search on a column.

        Args:
            table_name: Name of the table
            column_name: Name of the column to index

        Returns:
            bool: True if index was created successfully
        """
        try:
            # Create a generated column for text search
            await self.supabase.rpc(
                "execute_sql",
                {
                    "query": f"""
                ALTER TABLE {table_name} 
                ADD COLUMN IF NOT EXISTS searchable_{column_name} tsvector 
                GENERATED ALWAYS AS (to_tsvector('english', {column_name})) STORED;
                """
                },
            ).execute()

            # Create GIN index
            await self.supabase.rpc(
                "execute_sql",
                {
                    "query": f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name}_search 
                ON {table_name} USING gin(searchable_{column_name});
                """
                },
            ).execute()

            return True
        except Exception as e:
            self._logger.error(f"Failed to create search index: {e}")
            return False

    @make_sync
    async def bulk_insert_sync(self, *args, **kwargs):
        return await self.bulk_insert(*args, **kwargs)

    @make_sync
    async def move_file_sync(self, *args, **kwargs):
        return await self.move_file(*args, **kwargs)

    @make_sync
    async def subscribe_to_channel_sync(self, *args, **kwargs):
        return await self.subscribe_to_channel(*args, **kwargs)

    @make_sync
    async def subscribe_to_table_sync(self, *args, **kwargs):
        return await self.subscribe_to_table(*args, **kwargs)

    # Sync versions of all async methods
    @make_sync
    async def select_from_table_sync(self, *args, **kwargs):
        return await self.select_from_table(*args, **kwargs)

    @make_sync
    async def update_table_sync(self, *args, **kwargs):
        return await self.update_table(*args, **kwargs)

    @make_sync
    async def insert_into_table_sync(self, *args, **kwargs):
        return await self.insert_into_table(*args, **kwargs)

    @make_sync
    async def delete_from_table_sync(self, *args, **kwargs):
        return await self.delete_from_table(*args, **kwargs)

    @make_sync
    async def login_sync(self, *args, **kwargs):
        return await self.login(*args, **kwargs)

    @make_sync
    async def logout_sync(self, *args, **kwargs):
        return await self.logout(*args, **kwargs)

    @make_sync
    async def reset_password_sync(self, *args, **kwargs):
        return await self.reset_password(*args, **kwargs)

    @make_sync
    async def signup_sync(self, *args, **kwargs):
        return await self.signup(*args, **kwargs)

    @make_sync
    async def get_user_sync(self, *args, **kwargs):
        return await self.get_user(*args, **kwargs)

    @make_sync
    async def set_current_domain_sync(self, *args, **kwargs):
        return await self.set_current_domain(*args, **kwargs)

    @make_sync
    async def upload_file_sync(self, *args, **kwargs):
        return await self.upload_file(*args, **kwargs)

    @make_sync
    async def download_file_sync(self, *args, **kwargs):
        return await self.download_file(*args, **kwargs)

    @make_sync
    async def delete_file_sync(self, *args, **kwargs):
        return await self.delete_file(*args, **kwargs)

    @make_sync
    async def list_files_sync(self, *args, **kwargs):
        return await self.list_files(*args, **kwargs)

    @make_sync
    async def login_with_provider_sync(self, *args, **kwargs):
        return await self.login_with_provider(*args, **kwargs)

    @make_sync
    async def refresh_session_sync(self, *args, **kwargs):
        return await self.refresh_session(*args, **kwargs)

    @make_sync
    async def update_user_sync(self, *args, **kwargs):
        return await self.update_user(*args, **kwargs)

    @make_sync
    async def get_user_roles_sync(self, *args, **kwargs):
        return await self.get_user_roles(*args, **kwargs)

    @make_sync
    async def check_permission_sync(self, *args, **kwargs):
        return await self.check_permission(*args, **kwargs)

    @make_sync
    async def create_bucket_sync(self, *args, **kwargs):
        return await self.create_bucket(*args, **kwargs)

    @make_sync
    async def get_bucket_sync(self, *args, **kwargs):
        return await self.get_bucket(*args, **kwargs)

    @make_sync
    async def list_buckets_sync(self, *args, **kwargs):
        return await self.list_buckets(*args, **kwargs)

    @make_sync
    async def delete_bucket_sync(self, *args, **kwargs):
        return await self.delete_bucket(*args, **kwargs)

    @make_sync
    async def empty_bucket_sync(self, *args, **kwargs):
        return await self.empty_bucket(*args, **kwargs)

    @make_sync
    async def rpc_sync(self, *args, **kwargs):
        return await self.rpc(*args, **kwargs)

    @make_sync
    async def update_password_sync(self, *args, **kwargs):
        return await self.update_password(*args, **kwargs)

    @make_sync
    async def verify_otp_sync(self, *args, **kwargs):
        return await self.verify_otp(*args, **kwargs)

    @make_sync
    async def set_session_sync(self, *args, **kwargs):
        return await self.set_session(*args, **kwargs)

    @make_sync
    async def create_search_index_sync(self, *args, **kwargs):
        return await self.create_search_index(*args, **kwargs)

    @make_sync
    async def cleanup_sync(self, *args, **kwargs):
        return await self.cleanup(*args, **kwargs)
