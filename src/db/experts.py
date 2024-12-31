import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.db.base_db import BaseDB
from src.services.supabase_service import SupabaseService


class Experts(BaseDB):
    def __init__(self, supabase_client):
        super().__init__()
        if not supabase_client:
            raise ValueError("Supabase client cannot be None")
        self.supabase = supabase_client
        self.table_name = "experts"
        self.alias_table_name = "citation_expert_aliases"

    async def _verify_connection(self):
        """Verify the Supabase connection is active"""
        try:
            await self.supabase.select_from_table(self.table_name, ["id"], [])
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify database connection: {str(e)}")
            raise ConnectionError("Could not establish database connection") from e

    async def _handle_db_operation(
        self, operation_name: str, operation_func, *args, **kwargs
    ):
        """Generic error handler for database operations"""
        try:
            if not self.supabase:
                raise ConnectionError("No database connection available")
            return await operation_func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in {operation_name}: {str(e)}")
            raise

    async def add(
        self,
        expert_name: str,
        full_name: str,
        email_address: str = None,
        additional_fields: dict = None,
    ) -> dict | None:
        if not expert_name or not full_name:
            raise ValueError("expert_name and full_name are required parameters")

        async def _add_operation():
            expert_data = {
                "expert_name": expert_name,
                "full_name": full_name,
                "email_address": email_address,
            }
            if additional_fields:
                expert_data.update(additional_fields)

            result = await self.supabase.insert_into_table(self.table_name, expert_data)
            if not result:
                raise ValueError("Failed to add expert")
            return result

        return await self._handle_db_operation("create expert", _add_operation)

    async def get_all(self, additional_fields: dict = None) -> list | None:
        async def _get_all_operation():
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

            result = await self.supabase.select_from_table(
                self.table_name, fields, [("is_active", "eq", True)]
            )
            if not result or len(result) == 0:
                raise ValueError("No experts found or policy prevented read")
            return result

        return await self._handle_db_operation("get all experts", _get_all_operation)

    async def get_plus_by_name(
        self, expert_name: str, optional_fields: dict = None
    ) -> dict | None:
        if not expert_name:
            raise ValueError("expert_name is a required parameter")

        async def _get_plus_by_name_operation():
            fields = ["id", "expert_name", "full_name", "starting_ref_id"]
            if optional_fields:
                fields.extend(optional_fields)

            result = await self.supabase.select_from_table(
                self.table_name, fields, [("expert_name", "eq", expert_name)]
            )
            if not result or len(result) == 0:
                raise ValueError("Expert not found")
            return result[0]

        return await self._handle_db_operation(
            "get expert by name", _get_plus_by_name_operation
        )

    async def get_by_id(self, expert_id: str) -> dict | None:
        if not expert_id:
            raise ValueError("expert_id is a required parameter")

        async def _get_by_id_operation():
            fields = "*"
            result = await self.supabase.select_from_table(
                self.table_name, fields, [("id", "eq", expert_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Expert not found")
            return result[0]

        return await self._handle_db_operation("get expert by id", _get_by_id_operation)

    async def update(self, expert_id: str, update_data: dict) -> dict | None:
        if not expert_id or not update_data:
            raise ValueError("expert_id and update_data are required parameters")

        async def _update_operation():
            update_data["updated_at"] = "now()"
            result = await self.supabase.update_table(
                self.table_name, update_data, [("id", "eq", expert_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Failed to update expert")
            return result

        return await self._handle_db_operation("update expert", _update_operation)

    async def delete(self, expert_id: str) -> bool:
        if not expert_id:
            raise ValueError("expert_id is a required parameter")

        async def _delete_operation():
            result = await self.supabase.delete_from_table(
                self.table_name, [("id", "eq", expert_id)]
            )
            if not result:
                raise ValueError("Failed to delete expert")
            return True

        return await self._handle_db_operation("delete expert", _delete_operation)

    async def add_alias(self, expert_name: str, alias_name: str) -> dict | None:
        if not expert_name or not alias_name:
            raise ValueError("expert_name and alias_name are required parameters")

        async def _add_alias_operation():
            expert_data = await self.get_plus_by_name(expert_name)
            if not expert_data:
                self.logger.error("Expert not found or policy prevented read.")
                return None

            # Check if alias already exists
            existing_alias = await self.supabase.select_from_table(
                self.alias_table_name,
                ["id", "expert_alias"],
                [("expert_alias", "eq", alias_name)],
            )

            if existing_alias:
                return existing_alias[0]

            result = await self.supabase.insert_into_table(
                self.alias_table_name,
                {"expert_alias": alias_name, "expert_uuid": expert_data["id"]},
            )
            if not result:
                raise ValueError("Failed to add alias")
            return result

        return await self._handle_db_operation("add alias", _add_alias_operation)

    async def get_aliases_by_expert_name(self, expert_name: str) -> list | None:
        if not expert_name:
            raise ValueError("expert_name is a required parameter")

        async def _get_aliases_by_expert_name_operation():
            expert_data = await self.get_plus_by_name(expert_name)
            if not expert_data:
                self.logger.error("Expert not found or policy prevented read.")
                return None

            result = await self.supabase.select_from_table(
                self.alias_table_name,
                ["id", "expert_alias"],
                [("expert_uuid", "eq", expert_data["id"])],
            )
            return result

        return await self._handle_db_operation(
            "get aliases by expert name", _get_aliases_by_expert_name_operation
        )

    async def delete_alias(self, alias_id: str) -> bool:
        if not alias_id:
            raise ValueError("alias_id is a required parameter")

        async def _delete_alias_operation():
            existing_alias = await self.supabase.select_from_table(
                self.alias_table_name, ["id"], [("id", "eq", alias_id)]
            )

            if not existing_alias:
                self.logger.info(
                    f"Alias with id {alias_id} not found - already deleted or never existed"
                )
                return True

            result = await self.supabase.delete_from_table(
                self.alias_table_name, [("id", "eq", alias_id)]
            )
            return result

        return await self._handle_db_operation("delete alias", _delete_alias_operation)

    async def do_crud_test(self):
        async def _crud_test_operation():
            self.logger.info("Starting CRUD test")

            # Test concurrent operations
            test_add = {
                "expert_name": "ExpertTest",
                "full_name": "Test Full Name",
                "email_address": "test@test.com",
                "expertise_area": "Machine Learning",
                "experience_years": 10,
                "bio": "This is a test bio",
            }

            # Run multiple operations concurrently
            expert_data, alias_data, aliases = await asyncio.gather(
                self.get_plus_by_name(
                    "Naviaux", ["expertise_area", "experience_years", "bio"]
                ),
                self.add_alias("Abernethy", "Abernathy"),
                self.get_aliases_by_expert_name("Bunnage"),
            )

            if expert_data:
                self.logger.info(f"Expert data: {expert_data}")

            if alias_data:
                self.logger.info(f"Alias data: {alias_data}")
                # Delete the test alias
                if "id" in alias_data:
                    await self.delete_alias(alias_data["id"])
                    self.logger.info("Alias deleted")

            self.logger.info(f"Aliases: {aliases}")

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
