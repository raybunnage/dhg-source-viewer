import os
import sys
from pathlib import Path
from dotenv import load_dotenv

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
        self._verify_connection()

    def _verify_connection(self):
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
        expert_name: str,
        full_name: str,
        email_address: str = None,
        additional_fields: dict = None,
    ) -> dict | None:
        # Validate required parameters
        if not expert_name or not full_name:
            raise ValueError("expert_name and full_name are required parameters")

        def _add_operation():
            expert_data = {
                "expert_name": expert_name,
                "full_name": full_name,
                "email_address": email_address,
            }
            if additional_fields:
                expert_data.update(additional_fields)

            result = self.supabase.insert_into_table(self.table_name, expert_data)
            if not result:
                raise ValueError("Failed to add expert")
            return result

        return self._handle_db_operation("create expert", _add_operation)

    def get_all(self, additional_fields: dict = None) -> list | None:
        def _get_all_operation():
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
            result = self.supabase.select_from_table(
                self.table_name, fields, [("is_active", "eq", True)]
            )
            if not result or len(result) == 0:
                raise ValueError("No experts found or policy prevented read")
            return result

        return self._handle_db_operation("get all experts", _get_all_operation)

    def get_plus_by_name(
        self, expert_name: str, optional_fields: dict = None
    ) -> dict | None:
        if not expert_name:
            raise ValueError("expert_name is a required parameter")

        def _get_plus_by_name_operation():
            fields = ["id", "expert_name", "full_name", "starting_ref_id"]
            if optional_fields:
                fields.extend(optional_fields)

            result = self.supabase.select_from_table(
                self.table_name,
                fields,
                [("expert_name", "eq", expert_name)],
            )
            if not result or len(result) == 0:
                raise ValueError("Expert not found")
            return result[0]

        return self._handle_db_operation(
            "get expert by name", _get_plus_by_name_operation
        )

    def get_by_id(self, expert_id: str) -> dict | None:
        if not expert_id:
            raise ValueError("expert_id is a required parameter")

        def _get_by_id_operation():
            fields = "*"
            result = self.supabase.select_from_table(
                self.table_name, fields, [("id", "eq", expert_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Expert not found")
            return result[0]

        return self._handle_db_operation("get expert by id", _get_by_id_operation)

    def update(self, expert_id: str, update_data: dict) -> dict | None:
        if not expert_id or not update_data:
            raise ValueError("expert_id and update_data are required parameters")

        def _update_operation():
            update_data["updated_at"] = "now()"
            result = self.supabase.update_table(
                self.table_name, update_data, [("id", "eq", expert_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Failed to update expert")
            return result

        return self._handle_db_operation("update expert", _update_operation)

    def delete(self, expert_id: str) -> bool:
        if not expert_id:
            raise ValueError("expert_id is a required parameter")

        def _delete_operation():
            result = self.supabase.delete_from_table(
                self.table_name, [("id", "eq", expert_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Failed to delete expert")
            return True

        return self._handle_db_operation("delete expert", _delete_operation)

    def add_alias(self, expert_name: str, alias_name: str) -> dict | None:
        if not expert_name or not alias_name:
            raise ValueError("expert_name and alias_name are required parameters")

        def _add_alias_operation():
            expert_data = self.get_plus_by_name(expert_name)
            if not expert_data:
                self.logger.error("Expert not found or policy prevented read.")
                return None

            # Check if alias already exists
            existing_alias = self.supabase.select_from_table(
                self.alias_table_name,
                ["expert_alias"],
                [("expert_alias", "eq", alias_name)],
            )

            if existing_alias:
                return existing_alias[0]

            result = self.supabase.insert_into_table(
                self.alias_table_name,
                {"expert_alias": alias_name, "expert_uuid": expert_data["id"]},
            )
            if not result:
                raise ValueError("Failed to add alias")
            return result

        return self._handle_db_operation("add alias", _add_alias_operation)

    def get_aliases_by_expert_name(self, expert_name: str) -> list | None:
        if not expert_name:
            raise ValueError("expert_name is a required parameter")

        def _get_aliases_by_expert_name_operation():
            expert_data = self.get_plus_by_name(expert_name)
            if not expert_data:
                self.logger.error("Expert not found or policy prevented read.")
                return None

            # Get aliases for the expert
            result = self.supabase.select_from_table(
                self.alias_table_name,
                ["expert_alias"],
                [("expert_uuid", "eq", expert_data["id"])],
            )
            return result

        return self._handle_db_operation(
            "get aliases by expert name", _get_aliases_by_expert_name_operation
        )

    def delete_alias(self, alias_id: str) -> bool:
        if not alias_id:
            raise ValueError("alias_id is a required parameter")

        def _delete_alias_operation():
            result = self.supabase.delete_from_table(
                self.alias_table_name, [("id", "eq", alias_id)]
            )
            if not result or len(result) == 0:
                raise ValueError("Failed to delete alias")
            return True

        return self._handle_db_operation("delete alias", _delete_alias_operation)

    def do_crud_test(self):
        def _crud_test_operation():
            self.logger.info("Starting CRUD test")

            # Test adding an expert
            test_add = {
                "expert_name": "ExpertTest",
                "full_name": "Test Full Name",
                "email_address": "test@test.com",
            }
            additional_fields = {
                "expertise_area": "Machine Learning",
                "experience_years": 10,
                "bio": "This is a test bio",
            }

            # Test get operations
            expert_name = "Naviaux"
            optional_fields = ["expertise_area", "experience_years", "bio"]
            expert_data = self.get_plus_by_name(expert_name, optional_fields)
            if expert_data:
                self.logger.info(
                    f"Expert data from get_expert_plus_by_name: {expert_data}"
                )
            else:
                self.logger.error("Read operation failed.")

            # Test update operation
            expert_id = "34acaa61-7fb4-4c02-b463-a55128e354f3"
            update_data = {"experience_years": 11}
            update_success = self.update(expert_id, update_data)
            if update_success:
                self.logger.info(
                    f"Update operation successful. Updated data: {update_success}"
                )
            else:
                self.logger.error("Update operation failed.")

            # Test get by ID
            expert_data = self.get_by_id(expert_id)
            self.logger.info(f"Expert data from get_expert_by_id: {expert_data}")

            # Test alias operations
            alias_data = self.add_alias("Abernethy", "Abernathy")
            self.logger.info(f"Alias data: {alias_data}")

            aliases = self.get_aliases_by_expert_name("Carter")
            self.logger.info(f"Aliases: {aliases}")

            # self.delete_alias(alias_data["id"])
            # self.logger.info("Alias deleted")

        return self._handle_db_operation("CRUD test", _crud_test_operation)


def test_crud_operations():
    # Initialize and load environment variables
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    # Verify environment variables are present
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

    # Initialize Supabase client
    supabase = SupabaseService(url, key)

    # Verify login credentials
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    if not email or not password:
        raise ValueError("Missing TEST_EMAIL or TEST_PASSWORD environment variables")

    # Login and verify success
    login_result = supabase.login(email, password)
    if not login_result:
        raise ValueError("Failed to login to Supabase")

    # Now create the expert service
    expert_service = Experts(supabase)
    expert_service.do_crud_test()


#    load_dotenv()
#     url = os.getenv("SUPABASE_URL")
#     key = os.getenv("SUPABASE_KEY")
#     supabase = SupabaseService(url, key)
#     email = os.getenv("TEST_EMAIL")
#     password = os.getenv("TEST_PASSWORD")
#     supabase.login(email, password)
#     data = supabase.select_from_table(
#         "uni_document_types",
#         [
#             "document_type",
#             "description",
#             "is_ai_generated",
#             "mime_type",
#             "file_extension",
#             "category",
#         ],
#         [("is_active", "eq", True)],
#     )

#     print(data)

if __name__ == "__main__":
    test_crud_operations()


#  CREATE TABLE "temp_experts" (
# 	"expert_id"	INTEGER,
# 	"expert_name"	TEXT,
# 	"starting_ref_id"	INTEGER, full_name TEXT, is_in_core_group INTEGER DEFAULT 0,
# 	PRIMARY KEY("expert_id")
# )

# CREATE TABLE public.experts (
#   id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
#   expert_name text NOT NULL,
#   full_name text NOT NULL,
#   starting_ref_id integer NULL,
#   is_in_core_group boolean DEFAULT false,
#   created_at timestamp with time zone DEFAULT now(),
#   updated_at timestamp with time zone DEFAULT now(),
#   created_by uuid NOT NULL,
#   updated_by uuid NOT NULL,
#   domain_id uuid NOT NULL,
#   user_id uuid NOT NULL,
#   expertise_area text NULL,
#   bio text NULL,
#   experience_years integer NULL,
#   CONSTRAINT experts_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES public.domains(id),
#   CONSTRAINT experts_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
# );

# -- ALTER TABLE public.experts ENABLE ROW LEVEL SECURITY;

# CREATE INDEX ON public.experts(domain_id);
# CREATE INDEX ON public.experts(user_id);

# CREATE OR REPLACE FUNCTION transfer_temp_experts_to_experts()
# INSERT INTO public.experts (expert_name, full_name, starting_ref_id, is_in_core_group, created_by, updated_by, domain_id, user_id)
#   SELECT
#     expert_name,
#     full_name,
#     starting_ref_id,
#     (is_in_core_group <> 0) AS is_in_core_group,
#     'f5972054-059e-4b1e-915e-268bcdcc94b9',
#     'f5972054-059e-4b1e-915e-268bcdcc94b9',
#     '752f3bf7-a392-4283-bd32-e3f0e530c205',
#     'f5972054-059e-4b1e-915e-268bcdcc94b9'
#   FROM public.temp_experts;
