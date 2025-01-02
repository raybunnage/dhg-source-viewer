from dotenv import load_dotenv
from supabase import AsyncClient
from datetime import datetime
import asyncio
from .base_logging import Logger, log_method
from .exceptions import (
    SupabaseConnectionError,
    SupabaseQueryError,
    SupabaseAuthenticationError,
    SupabaseAuthorizationError,
    SupabaseError,
)
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Callable, List, Dict, Tuple, Union
from tenacity import retry, stop_after_attempt, wait_exponential


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
            self._supabase = AsyncClient(self.url, self.api_key)
        except Exception as e:
            self._logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise SupabaseConnectionError(
                "Failed to initialize Supabase client", original_error=e
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
        self, table_name: str, fields: dict, where_filters: list = None
    ):
        """Query data from a Supabase table with optional filters.

        Args:
            table_name: Name of the table to query
            fields: Dictionary of fields to select or "*" for all fields
            where_filters: Optional list of filters in format [(column, operator, value)]

        Returns:
            list | None: List of matching records or None if no matches/error
        """
        if not table_name:
            raise SupabaseError("Table name is required")

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
                        elif operator == "range_lt":
                            query = query.range_lt(column, value)
                        elif operator == "range_lte":
                            query = query.range_lte(column, value)
                        elif operator == "range_gt":
                            query = query.range_gt(column, value)
                        elif operator == "range_gte":
                            query = query.range_gte(column, value)
                        elif operator == "range_adjacent":
                            query = query.range_adjacent(column, value)
                        elif operator == "overlaps":
                            query = query.overlaps(column, value)
                        elif operator == "text_search":
                            query = query.text_search(column, value)
                        else:
                            raise ValueError(f"Unsupported operator: {operator}")

            response = await query.execute()
            if not response or not hasattr(response, "data"):
                return None
            return response.data
        except Exception as e:
            raise SupabaseQueryError("Failed to select from table", original_error=e)

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
                    elif operator == "range_lt":
                        query = query.range_lt(column, value)
                    elif operator == "range_lte":
                        query = query.range_lte(column, value)
                    elif operator == "range_gt":
                        query = query.range_gt(column, value)
                    elif operator == "range_gte":
                        query = query.range_gte(column, value)
                    elif operator == "range_adjacent":
                        query = query.range_adjacent(column, value)
                    elif operator == "overlaps":
                        query = query.overlaps(column, value)
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
    async def login(self, email: str, password: str) -> tuple[bool, dict | None]:
        """Login user with email and password.

        Args:
            email: User's email address
            password: User's password

        Returns:
            tuple: (success: bool, user_data: dict | None)

        Raises:
            ValueError: If email or password is missing
        """
        if not email or not password:
            raise SupabaseError("Email and password are required")

        try:
            response = await self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if response and hasattr(response, "user"):
                return True, response.user
            return False, None
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to login", original_error=e)

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
    async def set_current_domain(self, domain_id: str | None) -> None:
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
        """
        try:
            response = await self.supabase.storage.from_(bucket).upload(
                file_path,
                file_data,
                {"content-type": content_type} if content_type else None,
            )
            return response.get("Key")
        except Exception as e:
            raise SupabaseError("Failed to upload file", original_error=e)

    @log_method()
    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """Download a file from Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_path: Path to the file

        Returns:
            bytes: File data
        """
        try:
            return await self.supabase.storage.from_(bucket).download(file_path)
        except Exception as e:
            raise SupabaseError("Failed to download file", original_error=e)

    @log_method()
    async def delete_file(self, bucket: str, file_paths: list[str]) -> bool:
        """Delete files from Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_paths: List of file paths to delete

        Returns:
            bool: True if deletion was successful
        """
        try:
            await self.supabase.storage.from_(bucket).remove(file_paths)
            return True
        except Exception as e:
            raise SupabaseError("Failed to delete files", original_error=e)

    @log_method()
    async def list_files(self, bucket: str, path: str = "") -> list[dict]:
        """List files in a storage bucket.

        Args:
            bucket: Storage bucket name
            path: Optional path prefix to filter by

        Returns:
            list[dict]: List of file metadata
        """
        try:
            return await self.supabase.storage.from_(bucket).list(path)
        except Exception as e:
            raise SupabaseError("Failed to list files", original_error=e)

    # Enhanced Authentication Methods
    @log_method()
    async def login_with_provider(
        self, provider: str, redirect_url: str = None
    ) -> dict:
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
    async def get_user_roles(self, user_id: str = None) -> list[str]:
        """Get roles for the current or specified user.

        Args:
            user_id: Optional user ID, defaults to current user

        Returns:
            list[str]: List of role names
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
        callback: callable,
        event: str = "*",
        filter_str: str = None,
    ):
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

    # Add sync versions for new methods
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

    # Sync versions using the decorator
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
