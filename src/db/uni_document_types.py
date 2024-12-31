import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService
from src.db.base_db import BaseDB


class DocumentTypes(BaseDB):
    def __init__(self, supabase_client):
        super().__init__()
        if not supabase_client:
            raise ValueError("Supabase client cannot be None")
        self.supabase = supabase_client
        self.table_name = "uni_document_types"
        self.alias_table_name = "document_type_aliases"

    async def _verify_connection(self) -> bool:
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
        document_type: str,
        description: str = None,
        mime_type: str = None,
        file_extension: str = None,
        category: str = None,
        is_ai_generated: bool = False,
        additional_fields: dict = None,
    ) -> dict | None:
        if not document_type:
            raise ValueError("document_type is required parameters")

        async def _add_operation():
            document_type_data = {
                "document_type": document_type,
                "description": description,
                "mime_type": mime_type,
                "file_extension": file_extension,
                "category": category,
                "is_ai_generated": is_ai_generated,
            }
            if additional_fields:
                document_type_data.update(additional_fields)

            result = await self.supabase.insert_into_table(
                self.table_name, document_type_data
            )
            if not result:
                raise ValueError("Failed to add document type")
            return result

        return await self._handle_db_operation("add_document_type", _add_operation)

    async def get_by_id(self, document_type_id: str) -> dict:
        if not document_type_id:
            raise ValueError("document_type_id is required parameter")

        async def _get_by_id_operation():
            fields = "*"
            result = await self.supabase.select_from_table(
                self.table_name, fields, [("id", "eq", document_type_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Document type not found")
            return result[0]

        return await self._handle_db_operation("get_by_id", _get_by_id_operation)

    async def update(self, document_type_id: str, update_data: dict) -> dict:
        if not document_type_id or not update_data:
            raise ValueError("document_type_id and update_data are required parameters")

        async def _update_operation():
            update_data["updated_at"] = "now()"
            result = await self.supabase.update_table(
                self.table_name, update_data, [("id", "eq", document_type_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Failed to update document type")
            return result

        return await self._handle_db_operation("update", _update_operation)

    async def get_all(self, additional_fields: dict = None) -> list:
        async def _get_all_operation():
            fields = [
                "id",
                "document_type",
                "description",
                "mime_type",
                "file_extension",
                "category",
                "is_ai_generated",
            ]
            if additional_fields:
                fields.extend(additional_fields)
            response = await self.supabase.select_from_table(
                self.table_name, fields, []
            )
            if not response or len(response) == 0:
                raise ValueError(
                    "Failed to retrieve document types or policy prevented read"
                )
            return response

        return await self._handle_db_operation("get_all", _get_all_operation)

    async def get_plus_by_name(
        self, document_type_name: str, optional_fields: dict = None
    ) -> dict:
        if not document_type_name:
            raise ValueError("document_type_name is required parameter")

        async def _get_plus_by_name_operation():
            fields = [
                "id",
                "document_type",
                "description",
                "mime_type",
                "file_extension",
                "category",
                "is_ai_generated",
            ]
            if optional_fields:
                fields.extend(optional_fields)
            response = await self.supabase.select_from_table(
                self.table_name,
                fields,
                [("document_type", "eq", document_type_name)],
            )
            if not response or len(response) == 0:
                raise ValueError("Document type not found or policy prevented read")
            return response[0]

        return await self._handle_db_operation(
            "get_plus_by_name", _get_plus_by_name_operation
        )

    async def delete(self, document_type_id: str) -> bool:
        if not document_type_id:
            raise ValueError("document_type_id is required parameter")

        async def _delete_operation():
            result = await self.supabase.delete_from_table(
                self.table_name, [("id", "eq", document_type_id)]
            )
            if not result:
                raise ValueError("Failed to delete document type")
            return True

        return await self._handle_db_operation("delete", _delete_operation)

    async def get_aliases_by_document_type_name(
        self, document_type_name: str
    ) -> list | None:
        if not document_type_name:
            raise ValueError("document_type_name is a required parameter")

        async def _get_aliases_operation():
            document_type_data = await self.get_plus_by_name(document_type_name)
            if not document_type_data:
                self.logger.error("Document type not found or policy prevented read.")
                return None

            result = await self.supabase.select_from_table(
                self.alias_table_name,
                ["id", "alias_name"],
                [("document_type_uuid", "eq", document_type_data["id"])],
            )
            return result

        return await self._handle_db_operation(
            "get aliases by document type", _get_aliases_operation
        )

    async def do_crud_test(self):
        async def _crud_test_operation():
            self.logger.info("Starting CRUD test")

            new_type = {
                "document_type": "Test Document",
                "description": "A test document type",
                "mime_type": "application/pdf",
                "file_extension": ".pdf",
                "category": "test",
                "is_ai_generated": False,
            }

            # First create the test document
            test_doc = await self.add(
                document_type=new_type["document_type"],
                description=new_type["description"],
                mime_type=new_type["mime_type"],
                file_extension=new_type["file_extension"],
                category=new_type["category"],
                is_ai_generated=new_type["is_ai_generated"],
            )

            self.logger.info(f"Created test document: {test_doc}")

            try:
                # Run multiple operations concurrently
                doc_type_data, all_types, aliases = await asyncio.gather(
                    self.get_plus_by_name(
                        "Test Document", ["category", "is_ai_generated"]
                    ),
                    self.get_all(["category", "is_ai_generated"]),
                    self.get_aliases_by_document_type_name("Test Document"),
                )

                if doc_type_data:
                    self.logger.info(f"Document type data: {doc_type_data}")

                if all_types:
                    self.logger.info(f"Number of document types: {len(all_types)}")

                self.logger.info(f"Aliases: {aliases}")

                # Clean up - delete the test document
                if test_doc and "id" in test_doc:
                    await self.delete(test_doc["id"])
                    self.logger.info("Test document deleted")

            except Exception as e:
                self.logger.error(f"Error during CRUD test: {str(e)}")
                # Ensure cleanup even if test fails
                if test_doc and "id" in test_doc:
                    await self.delete(test_doc["id"])
                raise

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

    document_types = DocumentTypes(supabase)
    await document_types.do_crud_test()


if __name__ == "__main__":
    asyncio.run(test_crud_operations())
