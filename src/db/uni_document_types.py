import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService
from src.db.base_db import BaseDB, ValidationError, RecordNotFoundError, DatabaseError


class DocumentTypes(BaseDB[Dict[str, Any]]):
    def __init__(self, supabase_client):
        super().__init__(supabase_client)
        self.table_name = "uni_document_types"
        self.alias_table_name = "document_type_aliases"
        self.logger.debug(f"Initialized DocumentTypes with table: {self.table_name}")

    async def _validate_data(self, data: Dict[str, Any]) -> bool:
        self.logger.debug(f"Validating document type data: {data}")

        required_fields = ["document_type"]
        for field in required_fields:
            if field not in data or data[field] is None:
                self.logger.error(f"Missing required field: {field}")
                raise ValidationError(f"Missing required field: {field}")

        type_validations: Dict[str, type] = {
            "document_type": str,
            "description": str,
            "mime_type": str,
            "file_extension": str,
            "category": str,
            "is_ai_generated": bool,
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
        document_type: str,
        description: Optional[str] = None,
        mime_type: Optional[str] = None,
        file_extension: Optional[str] = None,
        category: Optional[str] = None,
        is_ai_generated: bool = False,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        self.logger.debug(f"Adding document type: {document_type}")

        if not document_type:
            self.logger.error("document_type is required parameter")
            raise ValidationError("document_type is required parameter")

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
                self.logger.debug(f"Including additional fields: {additional_fields}")
                document_type_data.update(additional_fields)

            self.logger.debug(f"Checking if document type exists: {document_type}")
            existing = await self.supabase.select_from_table(
                self.table_name, ["id"], [("document_type", "eq", document_type)]
            )
            if existing and len(existing) > 0:
                self.logger.debug(f"Found existing document type: {existing[0]}")
                return existing[0]

            self.logger.debug("Creating new document type")
            result = await self.supabase.insert_into_table(
                self.table_name, document_type_data
            )
            if not result:
                self.logger.error("Failed to add document type")
                raise DatabaseError("Failed to add document type")

            self.logger.debug(f"Created new document type: {result}")
            return result

        return await self._handle_db_operation("add_document_type", _add_operation)

    async def get_by_id(self, document_type_id: str) -> Optional[Dict[str, Any]]:
        self.logger.debug(f"Getting document type by ID: {document_type_id}")

        if not document_type_id:
            self.logger.error("document_type_id is required parameter")
            raise ValidationError("document_type_id is required parameter")

        async def _get_by_id_operation():
            fields = "*"
            self.logger.debug(f"Querying document type with ID: {document_type_id}")
            result = await self.supabase.select_from_table(
                self.table_name, fields, [("id", "eq", document_type_id)]
            )
            if not result or len(result) == 0:
                self.logger.debug(
                    f"Document type not found with ID: {document_type_id}"
                )
                raise RecordNotFoundError("Document type not found")
            self.logger.debug(f"Found document type: {result[0]}")
            return result[0]

        return await self._handle_db_operation("get_by_id", _get_by_id_operation)

    async def update(self, document_type_id: str, data: dict) -> bool:
        """Update a document type"""
        try:
            serialized_data = self.supabase._serialize_data(data)
            result = (
                await self.supabase.client.table("document_types")
                .update(serialized_data)
                .eq("id", document_type_id)
                .execute()
            )
            return bool(result.data)
        except Exception as e:
            logging.error(f"Error updating document type: {e}")
            return False

    async def get_all(
        self, additional_fields: Optional[List[str]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        self.logger.debug("Getting all document types")

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
                self.logger.debug(f"Including additional fields: {additional_fields}")
                fields.extend(additional_fields)

            self.logger.debug("Executing get_all query")
            response = await self.supabase.select_from_table(
                self.table_name, fields, []
            )
            if not response or len(response) == 0:
                self.logger.debug("No document types found")
                raise RecordNotFoundError(
                    "No document types found or policy prevented read"
                )
            self.logger.debug(f"Found {len(response)} document types")
            return response

        return await self._handle_db_operation("get_all", _get_all_operation)

    async def get_by_name(
        self, document_type: str, optional_fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        self.logger.debug(f"Getting document type by name: {document_type}")

        if not document_type:
            self.logger.error("document_type is required parameter")
            raise ValidationError("document_type is required parameter")

        async def _get_by_name_operation():
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
                self.logger.debug(f"Including optional fields: {optional_fields}")
                fields.extend(optional_fields)

            self.logger.debug(f"Executing get_by_name query for: {document_type}")
            response = await self.supabase.select_from_table(
                self.table_name,
                fields,
                [("document_type", "eq", document_type)],
            )
            if not response or len(response) == 0:
                self.logger.debug(f"Document type not found: {document_type}")
                raise RecordNotFoundError(
                    "Document type not found or policy prevented read"
                )
            self.logger.debug(f"Found document type: {response[0]}")
            return response[0]

        return await self._handle_db_operation("get_by_name", _get_by_name_operation)

    async def delete(self, document_type_id: str) -> bool:
        self.logger.debug(
            f"Performing hard delete for document type: {document_type_id}"
        )

        if not document_type_id:
            self.logger.error("document_type_id is required parameter")
            raise ValidationError("document_type_id is required parameter")

        async def _delete_operation():
            # First verify the record exists
            existing = await self.supabase.select_from_table(
                self.table_name, ["id"], [("id", "eq", document_type_id)]
            )
            if not existing:
                self.logger.error(f"Document type not found: {document_type_id}")
                raise RecordNotFoundError(
                    f"Document type not found: {document_type_id}"
                )

            self.logger.debug(
                f"Executing hard delete for document type: {document_type_id}"
            )
            result = await self.supabase.delete_from_table(
                self.table_name, [("id", "eq", document_type_id)]
            )
            if not result:
                self.logger.error(f"Failed to delete document type: {document_type_id}")
                raise DatabaseError("Failed to delete document type")

            self.logger.debug(
                f"Successfully hard deleted document type: {document_type_id}"
            )
            return True

        return await self._handle_db_operation("delete", _delete_operation)

    async def get_aliases(self, document_type: str) -> Optional[List[Dict[str, Any]]]:
        self.logger.debug(f"Getting aliases for document type: {document_type}")

        if not document_type:
            self.logger.error("document_type is required parameter")
            raise ValidationError("document_type is a required parameter")

        async def _get_aliases_operation():
            self.logger.debug(f"Finding document type data for: {document_type}")
            document_type_data = await self.get_by_name(document_type)
            if not document_type_data:
                self.logger.error("Document type not found")
                raise RecordNotFoundError(f"Document type not found: {document_type}")

            self.logger.debug(f"Found document type: {document_type_data}")
            self.logger.debug("Querying aliases")
            result = await self.supabase.select_from_table(
                self.alias_table_name,
                ["id", "alias_name"],
                [("document_type_uuid", "eq", document_type_data["id"])],
            )
            self.logger.debug(f"Found {len(result) if result else 0} aliases")
            return result

        return await self._handle_db_operation("get aliases", _get_aliases_operation)

    async def do_crud_test(self):
        self.logger.debug("Starting CRUD test")

        async def _crud_test_operation():
            self.logger.info("Starting CRUD test")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_type = {
                "document_type": f"Test Document {timestamp}",
                "description": "A test document type",
                "mime_type": "application/pdf",
                "file_extension": ".pdf",
                "category": "test",
                "is_ai_generated": False,
            }
            self.logger.debug(f"Test document data: {new_type}")

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
                self.logger.debug("Running concurrent operations")
                doc_type_data, all_types, aliases = await asyncio.gather(
                    self.get_by_name("Test Document", ["category", "is_ai_generated"]),
                    self.get_all(["category", "is_ai_generated"]),
                    self.get_aliases("professional biography"),
                )

                if doc_type_data:
                    self.logger.info(f"Document type data: {doc_type_data}")

                if all_types:
                    self.logger.info(f"Number of document types: {len(all_types)}")

                self.logger.info(f"Aliases: {aliases}")

                if test_doc and "id" in test_doc:
                    self.logger.debug(f"Cleaning up test document: {test_doc['id']}")
                    await self.delete(test_doc["id"])
                    self.logger.info("Test document deleted")

            except Exception as e:
                self.logger.error(f"Error during CRUD test: {str(e)}")
                if test_doc and "id" in test_doc:
                    self.logger.debug("Attempting cleanup after error")
                    await self.delete(test_doc["id"])
                raise

            self.logger.info("CRUD test completed successfully")
            return True

        return await self._handle_db_operation("CRUD test", _crud_test_operation)

    async def add_alias(
        self, document_type: str, alias_name: str
    ) -> Optional[Dict[str, Any]]:
        if not document_type or not alias_name:
            self.logger.error("document_type and alias_name are required parameters")
            raise ValidationError(
                "document_type and alias_name are required parameters"
            )

        async def _add_alias_operation():
            # Get the document type first
            document_type_data = await self.get_by_name(document_type)
            if not document_type_data:
                self.logger.error(f"Document type not found with name: {document_type}")
                raise RecordNotFoundError(
                    f"Document type not found with name: {document_type}"
                )

            # Create the alias data
            alias_data = {
                "alias_name": alias_name,
                "document_type_uuid": document_type_data["id"],
            }

            # Check if alias already exists
            existing_alias = await self.supabase.select_from_table(
                self.alias_table_name,
                ["id", "alias_name"],
                [
                    ("alias_name", "eq", alias_name),
                    ("document_type_uuid", "eq", document_type_data["id"]),
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
