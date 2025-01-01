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

from src.db.base_db import BaseDB, ValidationError, RecordNotFoundError, DatabaseError
from src.services.supabase_service import SupabaseService


class Experts(BaseDB[Dict[str, Any]]):
    def __init__(self, supabase_client):
        super().__init__(supabase_client)
        self.table_name = "experts"
        self.alias_table_name = "citation_expert_aliases"
        self.logger.debug(f"Initialized Experts with table: {self.table_name}")

    async def _validate_data(self, data: Dict[str, Any]) -> bool:
        self.logger.debug(f"Validating expert data: {data}")

        required_fields = ["expert_name", "full_name"]
        for field in required_fields:
            if field not in data or data[field] is None:
                self.logger.error(f"Missing required field: {field}")
                raise ValidationError(f"Missing required field: {field}")

        type_validations: Dict[str, type] = {
            "expert_name": str,
            "full_name": str,
            "email_address": str,
            "starting_ref_id": int,
            "is_in_core_group": bool,
            "is_active": bool,
            "user_id": str,
        }

        for field, expected_type in type_validations.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    self.logger.error(
                        f"Invalid type for {field}: expected {expected_type.__name__}"
                    )
                    raise ValidationError(f"{field} must be a {expected_type.__name__}")

        self.logger.debug("Data validation successful")
        return True

    async def add(
        self,
        expert_name: str,
        full_name: str,
        email_address: Optional[str] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        self.logger.debug(f"Adding expert: {expert_name}, {full_name}")

        if not expert_name or not full_name:
            self.logger.error("expert_name and full_name are required parameters")
            raise ValidationError("expert_name and full_name are required parameters")

        async def _add_operation():
            # 1. Prepare data
            expert_data = {
                "expert_name": expert_name,
                "full_name": full_name,
                "email_address": email_address,
            }
            if additional_fields:
                self.logger.debug(f"Including additional fields: {additional_fields}")
                expert_data.update(additional_fields)

            # 2. Validate data (matching DocumentTypes order)
            await self._validate_data(expert_data)

            # 3. Check if expert exists
            self.logger.debug(f"Checking if expert exists: {expert_name}")
            existing = await self.supabase.select_from_table(
                self.table_name, ["id"], [("expert_name", "eq", expert_name)]
            )

            if existing and len(existing) > 0:
                self.logger.debug(f"Found existing expert: {existing[0]}")
                return await self.get_by_id(existing[0]["id"])

            # 4. Insert new record
            self.logger.debug("Expert not found, creating new record")
            result = await self.supabase.insert_into_table(self.table_name, expert_data)
            if not result:
                self.logger.error("Failed to add expert")
                raise DatabaseError("Failed to add expert")
            self.logger.debug(f"Created new expert: {result}")
            return result

        return await self._handle_db_operation("add expert", _add_operation)

    async def get_all(
        self, additional_fields: Optional[List[str]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        self.logger.debug("Getting all experts")
        fields = [
            "id",
            "user_id",
            "expert_name",
            "full_name",
            "email_address",
            "is_in_core_group",
        ]

        if additional_fields:
            self.logger.debug(f"Including additional fields: {additional_fields}")
            fields.extend(additional_fields)

        async def _get_all_operation():
            self.logger.debug("Executing get_all query")
            result = await self.supabase.select_from_table(self.table_name, fields)
            if not result:
                self.logger.debug("No experts found")
                raise RecordNotFoundError("No experts found or policy prevented read")
            self.logger.debug(f"Found {len(result)} experts")
            return result

        return await self._handle_db_operation("get all experts", _get_all_operation)

    async def get_by_name(
        self, expert_name: str, optional_fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        self.logger.debug(f"Getting expert by name: {expert_name}")

        if not expert_name:
            self.logger.error("Expert name is required")
            raise ValidationError("expert_name is required")

        fields = ["id", "expert_name", "full_name", "starting_ref_id"]
        if optional_fields:
            self.logger.debug(f"Including optional fields: {optional_fields}")
            fields.extend(optional_fields)

        async def _get_by_name_operation():
            self.logger.debug(f"Executing get_by_name query for: {expert_name}")
            result = await self.supabase.select_from_table(
                self.table_name, fields, [("expert_name", "eq", expert_name)]
            )
            if not result:
                self.logger.debug(f"Expert not found: {expert_name}")
                raise RecordNotFoundError(f"Expert not found: {expert_name}")
            self.logger.debug(f"Found expert: {result[0]}")
            return result[0]

        return await self._handle_db_operation(
            "get expert by name", _get_by_name_operation
        )

    async def get_aliases(self, expert_name: str) -> Optional[List[Dict[str, Any]]]:
        self.logger.debug(f"Getting aliases for expert: {expert_name}")

        if not expert_name:
            self.logger.error("expert_name is required parameter")
            raise ValidationError("expert_name is a required parameter")

        async def _get_aliases_operation():
            self.logger.debug(f"Finding expert data for: {expert_name}")
            expert_data = await self.get_by_name(expert_name)
            if not expert_data:
                self.logger.error("Expert not found")
                raise RecordNotFoundError(f"Expert not found: {expert_name}")

            self.logger.debug(f"Found expert: {expert_data}")
            self.logger.debug("Querying aliases")
            result = await self.supabase.select_from_table(
                self.alias_table_name,
                ["id", "alias_name"],
                [("expert_uuid", "eq", expert_data["id"])],
            )
            self.logger.debug(f"Found {len(result) if result else 0} aliases")
            return result

        return await self._handle_db_operation("get aliases", _get_aliases_operation)

    async def add_alias(
        self, expert_name: str, alias_name: str
    ) -> Optional[Dict[str, Any]]:
        if not expert_name or not alias_name:
            self.logger.error("expert_name and alias_name are required parameters")
            raise ValidationError("expert_name and alias_name are required parameters")

        async def _add_alias_operation():
            # Get the expert first
            expert_data = await self.get_by_name(expert_name)
            if not expert_data:
                self.logger.error(f"Expert not found with name: {expert_name}")
                raise RecordNotFoundError(f"Expert not found with name: {expert_name}")

            # Create the alias data
            alias_data = {
                "alias_name": alias_name,
                "expert_uuid": expert_data["id"],
            }

            # Check if alias already exists
            existing_alias = await self.supabase.select_from_table(
                self.alias_table_name,
                ["id", "alias_name"],
                [
                    ("alias_name", "eq", alias_name),
                    ("expert_uuid", "eq", expert_data["id"]),
                ],
            )

            if existing_alias:
                return existing_alias[0]

            # Insert the new alias
            result = await self.supabase.insert_into_table(
                self.alias_table_name, alias_data
            )

            if not result:
                self.logger.error("Failed to add alias")
                raise DatabaseError("Failed to add alias")
            return result

        return await self._handle_db_operation("add alias", _add_alias_operation)

    async def delete_alias(self, alias_id: str) -> bool:
        if not alias_id:
            self.logger.error("alias_id is a required parameter")
            raise ValidationError("alias_id is a required parameter")

        async def _delete_alias_operation():
            existing_alias = await self.supabase.select_from_table(
                self.alias_table_name, ["id"], [("id", "eq", alias_id)]
            )

            if not existing_alias:
                self.logger.debug(f"Alias with id {alias_id} not found")
                raise RecordNotFoundError(f"Alias with id {alias_id} not found")

            result = await self.supabase.delete_from_table(
                self.alias_table_name, [("id", "eq", alias_id)]
            )
            if not result:
                self.logger.error(f"Failed to delete alias: {alias_id}")
                raise DatabaseError(f"Failed to delete alias: {alias_id}")
            return result

        return await self._handle_db_operation("delete alias", _delete_alias_operation)

    async def update(
        self, expert_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        self.logger.debug(f"Updating expert {expert_id} with data: {update_data}")

        async def _update_operation():
            result = await super().update(expert_id, update_data)
            if not result:
                self.logger.error(f"Failed to update expert: {expert_id}")
                raise DatabaseError("Failed to update expert")
            self.logger.debug(f"Successfully updated expert: {result}")
            return result

        return await self._handle_db_operation("update expert", _update_operation)

    async def delete(self, expert_id: str) -> bool:
        self.logger.debug(f"Performing hard delete for expert: {expert_id}")

        if not expert_id:
            self.logger.error("expert_id is required parameter")
            raise ValidationError("expert_id is required parameter")

        async def _delete_operation():
            # First verify the record exists
            existing = await self.supabase.select_from_table(
                self.table_name, ["id"], [("id", "eq", expert_id)]
            )
            if not existing:
                self.logger.error(f"Expert not found: {expert_id}")
                raise RecordNotFoundError(f"Expert not found: {expert_id}")

            self.logger.debug(f"Executing hard delete for expert: {expert_id}")
            result = await self.supabase.delete_from_table(
                self.table_name, [("id", "eq", expert_id)]
            )
            if not result:
                self.logger.error(f"Failed to delete expert: {expert_id}")
                raise DatabaseError("Failed to delete expert")

            self.logger.debug(f"Successfully hard deleted expert: {expert_id}")
            return True

        return await self._handle_db_operation("delete", _delete_operation)

    async def do_crud_test(self):
        self.logger.debug("Starting CRUD test")

        async def _crud_test_operation():
            self.logger.info("Starting CRUD test")

            test_expert = {
                "expert_name": "TestExpert5",
                "full_name": "Test Expert Name",
                "email_address": "test2@example.com",
            }
            self.logger.debug(f"Test expert data: {test_expert}")

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

            self.logger.info("CRUD test completed successfully")
            return True

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
