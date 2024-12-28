import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

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
        # Verify connection on initialization
        self._verify_connection()

    def _verify_connection(self) -> bool:
        """Verify the Supabase connection is active"""
        try:
            # Simple query to test connection without limit parameter
            self.supabase.select_from_table(self.table_name, ["id"], [])
            return True
        except Exception as e:
            self.logger.error(f"Failed to verify database connection: {str(e)}")
            raise ConnectionError("Could not establish database connection") from e

    def _handle_db_operation(
        self, operation_name: str, operation_func, *args, **kwargs
    ):
        """Generic error handler for database operations"""
        try:
            if not self.supabase:
                raise ConnectionError("No database connection available")
            return operation_func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in {operation_name}: {str(e)}")
            raise

    def add(
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

        def _add_operation():
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

            result = self.supabase.insert_into_table(
                self.table_name, document_type_data
            )
            if not result:
                raise ValueError("Failed to add document type")
            return result

        return self._handle_db_operation("add_document_type", _add_operation)

    def get_by_id(self, document_type_id: str) -> dict:
        if not document_type_id:
            raise ValueError("document_type_id is required parameter")

        def _get_by_id_operation():
            fields = "*"
            result = self.supabase.select_from_table(
                self.table_name, fields, [("id", "eq", document_type_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Document type not found")
            return result[0]

        return self._handle_db_operation("get_by_id", _get_by_id_operation)

    def update(self, document_type_id: str, update_data: dict) -> dict:
        if not document_type_id or not update_data:
            raise ValueError("document_type_id and update_data are required parameters")

        def _update_operation():
            update_data["updated_at"] = "now()"
            result = self.supabase.update_table(
                self.table_name, update_data, [("id", "eq", document_type_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Failed to update document type")
            return result

        return self._handle_db_operation("update", _update_operation)

    def get_all(self, additional_fields: dict = None) -> list:
        def _get_all_operation():
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
            response = self.supabase.select_from_table(self.table_name, fields, [])
            if not response or len(response) == 0:
                raise ValueError(
                    "Failed to retrieve document types or policy prevented read"
                )
            return response

        return self._handle_db_operation("get_all", _get_all_operation)

    def get_plus_by_name(
        self, document_type_name: str, optional_fields: dict = None
    ) -> dict:
        if not document_type_name:
            raise ValueError("document_type_name is required parameter")

        def _get_plus_by_name_operation():
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
            response = self.supabase.select_from_table(
                self.table_name,
                fields,
                [("document_type", "eq", document_type_name)],
            )
            if not response or len(response) == 0:
                raise ValueError("Document type not found or policy prevented read")
            return response[0]

        return self._handle_db_operation(
            "get_plus_by_name", _get_plus_by_name_operation
        )

    def delete(self, document_type_id: str) -> bool:
        if not document_type_id:
            raise ValueError("document_type_id is required parameter")

        def _delete_operation():
            result = self.supabase.delete_from_table(
                self.table_name, [("id", "eq", document_type_id)]
            )
            if not result:
                raise ValueError("Failed to delete document type")
            return True

        return self._handle_db_operation("delete", _delete_operation)

    def get_aliases_by_document_type_name(self, document_type_name: str) -> list | None:
        if not document_type_name:
            raise ValueError("document_type_name is a required parameter")

        def _get_aliases_by_expert_name_operation():
            document_type_data = self.get_plus_by_name(document_type_name)
            if not document_type_data:
                self.logger.error("Document type not found or policy prevented read.")
                return None

            # Get aliases for the expert
            result = self.supabase.select_from_table(
                self.alias_table_name,
                ["id", "alias_name"],
                [("document_type_uuid", "eq", document_type_data["id"])],
            )
            return result

        return self._handle_db_operation(
            "get aliases by expert name", _get_aliases_by_expert_name_operation
        )

    def do_crud_test(self):
        def _crud_test_operation():
            self.logger.info("Starting CRUD test")
            # Create a document type
            new_type = {
                "document_type": "Test Document",
                "description": "A test document type",
                "mime_type": "application/pdf",
                "file_extension": ".pdf",
                "category": "test",
                "is_ai_generated": False,
            }

            test_add = self.add(
                new_type["document_type"],
                new_type["description"],
                new_type["mime_type"],
                new_type["file_extension"],
                new_type["category"],
                new_type["is_ai_generated"],
            )
            self.logger.info(f"Test add: {test_add}")

            # Read and verify other operations
            doc_type_name = new_type["document_type"]
            optional_fields = ["category", "is_ai_generated"]
            doc_type_data = self.get_plus_by_name(doc_type_name, optional_fields)
            self.logger.info(
                f"Document type data from get_plus_by_name: {doc_type_data}"
            )

            all_doc_types = self.get_all(["category", "is_ai_generated"])
            self.logger.info(f"Number of document types: {len(all_doc_types)}")

            # Update and verify
            doc_type_id = doc_type_data["id"]
            update_data = {"description": "Updated test description"}
            update_success = self.update(doc_type_id, update_data)
            self.logger.info(
                f"Update operation successful. Updated data: {update_success}"
            )

            # Verify update
            updated_doc = self.get_plus_by_name(doc_type_name, optional_fields)
            self.logger.info(f"Updated document type data: {updated_doc}")

            # Test delete
            delete_success = self.delete(doc_type_id)
            if not delete_success:
                raise ValueError("Delete operation failed")
            self.logger.info("Delete operation successful.")

            return True

        return self._handle_db_operation("do_crud_test", _crud_test_operation)


def test_crud_operations():
    # Initialize  load_dotenv()
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)
    document_types = DocumentTypes(supabase)
    document_types.do_crud_test()


if __name__ == "__main__":
    test_crud_operations()
