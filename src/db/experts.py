import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.db.base_db import BaseDB, ValidationError, RecordNotFoundError
from src.services.supabase_service import SupabaseService


class Experts(BaseDB[Dict[str, Any]]):
    def __init__(self, supabase_client):
        super().__init__(supabase_client)
        self.table_name = "experts"
        self.alias_table_name = "citation_expert_aliases"

    async def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Implement required abstract method for data validation"""
        required_fields = ["expert_name", "full_name"]
        return all(field in data and data[field] for field in required_fields)

    # Modified add method to use base functionality
    async def add(
        self,
        expert_name: str,
        full_name: str,
        email_address: str = None,
        additional_fields: dict = None,
    ) -> Optional[Dict[str, Any]]:
        expert_data = {
            "expert_name": expert_name,
            "full_name": full_name,
            "email_address": email_address,
        }
        if additional_fields:
            expert_data.update(additional_fields)

        # Check if expert already exists
        try:
            existing = await self.get_by_name(expert_name)
            return existing
        except RecordNotFoundError:
            return await super().add(expert_data)

    # Simplified get_all using base functionality
    async def get_all(
        self, additional_fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        fields = [
            "id",
            "user_id",
            "expert_name",
            "full_name",
            "email_address",
            "is_in_core_group",
        ]
        if additional_fields:
            fields.extend(additional_fields)

        async def _get_all_operation():
            result = await self.supabase.select_from_table(
                self.table_name, fields, [("is_active", "eq", True)]
            )
            if not result:
                return []
            return result

        return await self._handle_db_operation("get all experts", _get_all_operation)

    # Renamed for clarity and consistency
    async def get_by_name(
        self, expert_name: str, optional_fields: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get expert by name (formerly get_plus_by_name)"""
        if not expert_name:
            raise ValidationError("expert_name is required")

        fields = ["id", "expert_name", "full_name", "starting_ref_id"]
        if optional_fields:
            fields.extend(optional_fields)

        async def _get_by_name_operation():
            result = await self.supabase.select_from_table(
                self.table_name, fields, [("expert_name", "eq", expert_name)]
            )
            if not result:
                raise RecordNotFoundError(f"Expert not found: {expert_name}")
            return result[0]

        return await self._handle_db_operation(
            "get expert by name", _get_by_name_operation
        )

    # Alias-related methods
    async def add_alias(
        self, expert_name: str, alias_name: str
    ) -> Optional[Dict[str, Any]]:
        if not expert_name or not alias_name:
            raise ValidationError("expert_name and alias_name are required")

        async def _add_alias_operation():
            expert_data = await self.get_by_name(expert_name)
            alias_data = {"alias_name": alias_name, "expert_uuid": expert_data["id"]}

            # Check existing alias
            try:
                existing = await self.get_alias(alias_name, expert_data["id"])
                return existing
            except RecordNotFoundError:
                result = await self.supabase.insert_into_table(
                    self.alias_table_name, alias_data
                )
                if not result:
                    raise ValidationError("Failed to add alias")
                return result

        return await self._handle_db_operation("add alias", _add_alias_operation)

    async def get_alias(
        self, alias_name: str, expert_id: str
    ) -> Optional[Dict[str, Any]]:
        """Helper method to get a specific alias"""
        result = await self.supabase.select_from_table(
            self.alias_table_name,
            ["id", "alias_name"],
            [
                ("alias_name", "eq", alias_name),
                ("expert_uuid", "eq", expert_id),
            ],
        )
        if not result:
            raise RecordNotFoundError("Alias not found")
        return result[0]

    # Test method updated to use new base functionality
    async def do_crud_test(self):
        """Test CRUD operations using base class methods"""

        async def _crud_test_operation():
            self.logger.info("Starting CRUD test")

            # Test data
            test_expert = {
                "expert_name": "TestExpert",
                "full_name": "Test Expert Name",
                "email_address": "test@example.com",
            }

            # Create
            expert = await self.add(**test_expert)
            self.logger.info(f"Created test expert: {expert}")

            # Read
            retrieved = await self.get_by_id(expert["id"])
            self.logger.info(f"Retrieved expert: {retrieved}")

            # Update
            updated = await self.update(
                expert["id"], {"email_address": "updated@example.com"}
            )
            self.logger.info(f"Updated expert: {updated}")

            # Delete (soft)
            await self.delete(expert["id"])
            self.logger.info("Soft deleted expert")

            # Test alias operations
            alias = await self.add_alias(test_expert["expert_name"], "TestAlias")
            self.logger.info(f"Created alias: {alias}")

        return await self._handle_db_operation("CRUD test", _crud_test_operation)


async def test_crud_operations():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    supabase = SupabaseService(url, key)
    await supabase.login(email, password)

    expert_service = Experts(supabase)
    await expert_service.do_crud_test()


if __name__ == "__main__":
    asyncio.run(test_crud_operations())


def main():
    """Test the Supabase service."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)
    # Then create the service with the client
    todos = supabase.get_todos()
    if todos:
        print(f"Found {len(todos.data)} todos")
    else:
        print("No todos found or error occurred")

    users = supabase.get_test_users()
    if users:
        print(f"Found {len(users.data)} users")
    else:
        print("No users found or error occurred")


def update_document_type_description():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)

    try:
        response = supabase.update_table(
            "uni_document_types",
            {"description": "includes master's thesis"},
            [("document_type", "eq", "thesis")],
        )
        if response.status_code == 200:
            print("Document type description updated successfully.")
        else:
            print(
                f"Failed to update document type description. Status code: {response.status_code}"
            )
    except Exception as e:
        print(f"Error updating document type description: {str(e)}")


def insert_test():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)

    new_expert = {
        "expert_name": "John Doe",
        "full_name": "Johnathan Doe",
        "starting_ref_id": 123,
        "expertise_area": "AI",
        "experience_years": 5,
        "user_id": "f5972054-059e-4b1e-915e-268bcdcc94b9",
    }
    try:
        response = supabase.insert_into_table("experts", new_expert)
        if response:  # If we got back a dict with the inserted data
            print("New expert inserted successfully.")
            print(f"Inserted expert data: {response}")
        else:
            print("Failed to insert new expert.")
    except Exception as e:
        print(f"Error inserting new expert: {str(e)}")


def select_from_table():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)
    data = supabase.select_from_table(
        "uni_document_types",
        [
            "document_type",
            "description",
            "is_ai_generated",
            "mime_type",
            "file_extension",
            "category",
        ],
        [("is_active", "eq", True)],
    )
    print(data)
    fields = "*"
    expert_id = "34acaa61-7fb4-4c02-b463-a55128e354f3"
    data = supabase.select_from_table(
        "experts",
        fields,
        [("id", "eq", expert_id)],
    )
    print(data)

