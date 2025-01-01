import os
from dotenv import load_dotenv
from supabase import AsyncClient
from datetime import datetime
import logging
from pathlib import Path
import asyncio
import pytest
from uuid import uuid4


class SupabaseService:
    def __init__(self, url: str, api_key: str, log_level=logging.DEBUG):
        self.url = url
        self.api_key = api_key
        self.setup_logging(log_level)
        self._init_client()

    def setup_logging(self, log_level):
        """Configure logging with file and console handlers"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create a logger for this instance
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

        # Only add handlers if they haven't been added yet
        if not self.logger.handlers:
            # File handler - separate file for each day
            file_handler = logging.FileHandler(
                log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter("%(name)s - %(levelname)s - %(message)s")
            )

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def _init_client(self) -> None:
        """Initialize the Supabase async client"""
        try:
            self._supabase = AsyncClient(self.url, self.api_key)
            self.logger.info("Supabase client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise

    @property
    def supabase(self) -> AsyncClient:
        """Ensure we always have a valid Supabase client."""
        if not hasattr(self, "_supabase") or not isinstance(
            self._supabase, AsyncClient
        ):
            self.logger.error("Supabase client not properly initialized")
            raise RuntimeError("Supabase client not properly initialized")
        return self._supabase

    async def select_from_table(
        self, table_name: str, fields: dict, where_filters: list = None
    ):
        if not table_name:
            self.logger.error("Table name is required")
            raise ValueError("Table name is required")

        try:
            self.logger.debug(f"Selecting from table {table_name} with fields {fields}")
            if fields == "*":
                query = self.supabase.table(table_name).select("*")
            else:
                query = self.supabase.table(table_name).select(",".join(fields))

            if where_filters:
                self.logger.debug(f"Applying filters: {where_filters}")
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
                        self.logger.error(f"Unsupported operator: {operator}")
                        raise ValueError(f"Unsupported operator: {operator}")

            response = await query.execute()
            if not response or not hasattr(response, "data"):
                self.logger.error("Invalid response format from Supabase")
                return None
            self.logger.debug(f"Successfully retrieved {len(response.data)} records")
            return response.data
        except Exception as e:
            self.logger.error(f"Select error: {str(e)}")
            return None

    async def update_table(
        self, table_name: str, update_fields: dict, where_filters: list
    ) -> dict | None:
        """Update records matching the filter and return the updated record."""
        if not table_name:
            self.logger.error("Table name is required")
            raise ValueError("Table name is required")

        try:
            # Serialize datetime fields before update
            serialized_fields = self._serialize_data(update_fields)
            self.logger.debug(
                f"Updating table {table_name} with fields {serialized_fields}"
            )

            query = self.supabase.table(table_name).update(serialized_fields)

            if where_filters:
                self.logger.debug(f"Applying filters: {where_filters}")
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
                        self.logger.error(f"Unsupported operator: {operator}")
                        raise ValueError(f"Unsupported operator: {operator}")

            response = await query.execute()
            if response.data and len(response.data) > 0:
                self.logger.debug("Update successful")
                return response.data[0]  # Return first updated record
            self.logger.warning("No records updated")
            return None
        except Exception as e:
            self.logger.error(f"Update error: {str(e)}")
            return None

    async def insert_into_table(
        self, table_name: str, insert_fields: dict, upsert: bool = False
    ) -> dict | None:
        if not table_name:
            self.logger.error("Table name is required")
            raise ValueError("Table name is required")

        try:
            self.logger.debug(f"Inserting into table {table_name}: {insert_fields}")
            query = self.supabase.table(table_name)
            if upsert:
                self.logger.debug("Using upsert operation")
                response = await query.upsert(insert_fields).execute()
            else:
                response = await query.insert(insert_fields).execute()

            if response.data and len(response.data) > 0:
                self.logger.debug("Insert successful")
                return response.data[0]
            self.logger.warning("No records inserted")
            return None
        except Exception as e:
            self.logger.error(f"Insert error: {str(e)}")
            return None

    async def delete_from_table(self, table_name: str, where_filters: list) -> bool:
        """Delete records matching the filter."""
        try:
            self.logger.debug(
                f"Deleting from table {table_name} with filters {where_filters}"
            )
            query = self.supabase.table(table_name).delete()

            for column, operator, value in where_filters:
                if operator == "eq":
                    query = query.eq(column, value)
                # ... other operators ...

            response = await query.execute()
            success = bool(response.data)
            if success:
                self.logger.debug("Delete successful")
            else:
                self.logger.warning("No records deleted")
            return success
        except Exception as e:
            self.logger.error(f"Delete error: {str(e)}")
            return False

    async def login(self, email: str, password: str):
        try:
            self.email = email
            self.password = password
            self.logger.info(f"Attempting login with email: {email}")
            data = await self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            self.session = data
            self.logger.info(f"Login successful for: {email}")
            return data
        except Exception as e:
            self.logger.error(f"Login error details: {str(e)}")
            return None

    async def logout(self):
        try:
            self.logger.info("Logging out user")
            await self.supabase.auth.sign_out()
            self.session = None
            self.logger.info("Logout successful")
        except Exception as e:
            self.logger.error(f"Logout error: {str(e)}")

    async def reset_password(self, email: str) -> bool:
        try:
            self.logger.info(f"Initiating password reset for: {email}")
            await self.supabase.auth.reset_password_for_email(email)
            self.logger.info(f"Password reset email sent to {email}")
            return True
        except Exception as e:
            self.logger.error(f"Password reset error: {str(e)}")
            return False

    async def signup(self, email: str, password: str):
        try:
            await self.supabase.auth.sign_up({"email": email, "password": password})
            self.logger.info(f"Signup successful for: {email}")
            return True
        except Exception as e:
            self.logger.error(f"Signup error: {str(e)}")
            return False

    def clear_logs(self):
        """Clear the current day's log file"""
        log_dir = Path("logs")
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        self.logger.debug(f"Clearing log file: {log_file}")
        with open(log_file, "w") as f:
            f.truncate(0)

    def _serialize_data(self, data: dict) -> dict:
        """Serialize data for Supabase by converting Python types to JSON-compatible types"""
        serialized = {}
        for key, value in data.items():
            if isinstance(value, bool):
                serialized[key] = str(value).lower()  # Convert bool to 'true'/'false'
            else:
                serialized[key] = value
        return serialized

    async def get_user(self):
        """Get the currently logged in user's details"""
        try:
            self.logger.debug("Fetching current user details")
            user = await self.supabase.auth.get_user()
            if user and hasattr(user, "user"):
                self.logger.debug(
                    f"Successfully retrieved user with ID: {user.user.id}"
                )
                return user.user
            self.logger.warning("No user currently logged in")
            return None
        except Exception as e:
            self.logger.error(f"Error getting user details: {str(e)}")
            return None

    async def set_current_domain(self, domain_id: str | None) -> None:
        """Set the current domain for subsequent Supabase operations."""
        try:
            self.logger.debug(f"Setting current domain to: {domain_id}")
            response = await self.supabase.rpc(
                "set_current_domain", {"domain_id": domain_id}
            ).execute()

            # Check if response has data attribute instead of error
            if hasattr(response, "data"):
                self.logger.debug("Successfully set current domain")
            else:
                self.logger.error("Failed to set current domain: Invalid response")
                raise Exception(
                    "Failed to set current domain: Invalid response from server"
                )

        except Exception as e:
            self.logger.error(f"Error setting current domain: {str(e)}")
            raise


async def insert_test_emails():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    supabase = SupabaseService(url, key)
    await supabase.login(email, password)

    # Test single record insert
    single_email = {
        "email_id": "1",
        "subject": "Test Email 1",
        "content": "This is a test email body 1",
        "sender": "sender1@test.com",
        "to_recipients": "recipient1@test.com",
        "date": datetime.now(),
        "created_at": datetime.now(),
    }

    try:
        response = await supabase.insert_into_table("temp_emails", single_email)
        print("Single test email inserted successfully")
        print(f"Inserted email data: {response}")
    except Exception as e:
        print(f"Error inserting single test email: {e}")

    # Test multiple records insert
    test_emails = [
        {
            "email_id": str(i),
            "subject": f"Test Email {i}",
            "content": f"This is a test email body {i}",
            "sender": f"sender{i}@test.com",
            "to_recipients": f"recipient{i}@test.com",
            "date": datetime.now(),
            "created_at": datetime.now(),
        }
        for i in range(2, 4)
    ]

    try:
        response = await supabase.insert_into_table("temp_emails", test_emails)
        print("Multiple test emails inserted successfully")
        print(f"Inserted email data: {response}")
    except Exception as e:
        print(f"Error inserting multiple test emails: {e}")


async def test_login_and_get_user():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    supabase = SupabaseService(url, key)

    # Attempt login
    login_response = await supabase.login(email, password)
    if not login_response:
        print("Login failed")
        return

    # Get user details
    user = await supabase.get_user()
    if user:
        print(f"Successfully retrieved user ID: {user.id}")
        print(f"User email: {user.email}")
    else:
        print("Failed to get user details")


async def test_domain_operations():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    supabase = SupabaseService(url, key)

    # Login first
    login_response = await supabase.login(email, password)
    if not login_response:
        print("Login failed")
        return

    # Test setting domain
    test_domain_id = str(uuid4())
    try:
        await supabase.set_current_domain(test_domain_id)
        print(f"Successfully set domain to: {test_domain_id}")
    except Exception as e:
        print(f"Failed to set domain: {e}")
        return

    # Verify domain was set by querying a domain-scoped table
    try:
        response = await supabase.select_from_table("some_domain_scoped_table", ["*"])
        print("Successfully queried domain-scoped table")
    except Exception as e:
        print(f"Error querying domain-scoped table: {e}")

    # Test clearing domain
    try:
        await supabase.set_current_domain(None)
        print("Successfully cleared domain")
    except Exception as e:
        print(f"Failed to clear domain: {e}")


if __name__ == "__main__":

    async def run_tests():
        # await test_login_and_get_user()
        await test_domain_operations()
        # await insert_test_emails()

    asyncio.run(run_tests())
