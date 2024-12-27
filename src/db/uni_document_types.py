import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService
from dotenv import load_dotenv
from typing import Optional
from src.db.base_db import BaseDB


class DocumentTypes(BaseDB):
    def __init__(self, supabase_client):
        super().__init__()  # Initialize BaseDB for domain-level logging
        self.supabase = supabase_client  # Composition instead of inheritance
        self.table_name = "uni_document_types"

    def add(
        self,
        document_type: str,
        description: str = None,
        mime_type: str = None,
        file_extension: str = None,
        category: str = None,
        is_ai_generated: bool = False,
        additional_fields: dict = None,
    ) -> dict:
        try:
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

            if result:
                return result
            else:
                self.logger.error("Failed to add document type")
                return None

        except Exception as e:
            self.logger.error(f"Error creating document type: {str(e)}")
            return None

    def get_by_id(self, document_type_id: str) -> dict:
        try:
            fields = "*"
            result = self.supabase.select_from_table(
                self.table_name, fields, [("id", "eq", document_type_id)]
            )
            if result and len(result) > 0:
                return result[0]
            self.logger.error("Document type not found.")
            return None

        except Exception as e:
            self.logger.error(f"Error getting document type: {str(e)}")
            return None

    def update(self, document_type_id: str, update_data: dict) -> dict:
        try:
            # Add updated timestamp
            update_data["updated_at"] = "now()"

            result = self.supabase.update_table(
                self.table_name, update_data, [("id", "eq", document_type_id)]
            )
            if result and len(result) > 0:
                return result
            self.logger.error("Failed to update document type.")
            return None

        except Exception as e:
            self.logger(f"Error updating document type: {str(e)}")
            return None

    def get_all(self, additional_fields: dict = None) -> list | None:
        try:
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
            if response and len(response) > 0:
                return response
            self.logger.error(
                "Failed to retrieve document types or policy prevented read."
            )
            return None

        except Exception as e:
            self.logger(f"Error getting document types: {str(e)}")
            return None

    def get_plus_by_name(
        self, document_type_name: str, optional_fields: dict = None
    ) -> dict | None:
        try:
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
            if response and len(response) > 0:
                return response[0]
            else:
                self.logger.error("Document type not found or policy prevented read.")
                return None
        except Exception as e:
            self.logger.error(f"Error reading document type: {str(e)}")
            return None

    def delete(self, document_type_id: str) -> bool:
        try:
            result = self.supabase.delete_from_table(
                self.table_name, [("id", "eq", document_type_id)]
            )
            if result:
                return True
            self.logger.error("Failed to delete document type.")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting document type: {str(e)}")
            return False

    def do_crud_test(self):
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

        # Read the document type
        doc_type_name = new_type["document_type"]
        optional_fields = ["category", "is_ai_generated"]
        doc_type_data = self.get_plus_by_name(doc_type_name, optional_fields)
        if doc_type_data:
            self.logger.info(
                f"Document type data from get_plus_by_name: {doc_type_data}"
            )
        else:
            self.logger.error("Read operation failed.")

        # Get all document types
        all_doc_types = self.get_all(["category", "is_ai_generated"])
        if all_doc_types:
            self.logger.info(f"Number of document types: {len(all_doc_types)}")
        else:
            self.logger.error("Failed to retrieve all document types")

        # Update the document type
        if doc_type_data:
            doc_type_id = doc_type_data["id"]
            update_data = {"description": "Updated test description"}
            update_success = self.update(doc_type_id, update_data)
            if update_success:
                self.logger.info(
                    f"Update operation successful. Updated data: {update_success}"
                )
            else:
                self.logger.error("Update operation failed.")

            # Verify update
            updated_doc = self.get_plus_by_name(doc_type_name, optional_fields)
            self.logger.info(f"Updated document type data: {updated_doc}")

            # Test delete
            delete_success = self.delete(doc_type_id)
            if delete_success:
                self.logger.info("Delete operation successful.")
            else:
                self.logger.error("Delete operation failed.")


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
