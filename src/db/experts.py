import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService
from dotenv import load_dotenv


class Experts:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def add_expert(
        self,
        expert_name: str,
        full_name: str,
        email_address: str = None,
        additional_fields: dict = None,
    ) -> dict | None:
        try:
            expert_data = {
                "expert_name": expert_name,
                "full_name": full_name,
                "email_address": email_address,
            }
            if additional_fields:
                expert_data.update(additional_fields)

            response = self.supabase.insert_into_table("experts", expert_data)
            if response:
                print("Expert created successfully.")
                return response
            else:
                print("Failed to create expert or policy prevented insert.")
                return None
        except Exception as e:
            print(f"Error creating expert: {str(e)}")
            return False

    def get_all_experts(self, additional_fields: dict = None) -> list | None:
        try:
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
            response = self.supabase.select_from_table(
                "experts", fields, [("is_active", "eq", True)]
            )
            if response and len(response) > 0:
                return response
            else:
                print("Failed to retrieve expert fields or policy prevented read.")
                return None

        except Exception as e:
            print(f"Error getting expert fields: {str(e)}")
            return None

    def get_expert_plus_by_name(
        self, expert_name: str, optional_fields: dict = None
    ) -> dict:
        try:
            fields = ["id", "expert_name", "full_name", "starting_ref_id"]
            if optional_fields:
                fields.extend(optional_fields)
            response = self.supabase.select_from_table(
                "experts",
                fields,
                [("expert_name", "eq", expert_name)],
            )
            if response and len(response) > 0:
                return response[0]
            else:
                print("Expert not found or policy prevented read.")
                return {}
        except Exception as e:
            print(f"Error reading expert: {str(e)}")
            return {}

    def get_expert_by_id(self, expert_id: str) -> dict | None:
        try:
            fields = "*"
            response = self.supabase.select_from_table(
                "experts",
                fields,
                [("id", "eq", expert_id)],
            )
            if response and len(response) > 0:
                return response[0]  # Return the dictionary of the result if successful
            else:
                print("Expert not found or policy prevented read.")
                return None
        except Exception as e:
            print(f"Error reading expert: {str(e)}")
            return None

    def update_expert(self, expert_id: str, update_data: dict) -> dict | None:
        try:
            response = self.supabase.update_table(
                "experts", update_data, [("id", "eq", expert_id)]
            )
            if response and len(response) > 0:
                print("Expert updated successfully.")
                return response  # Return the entire record if successful
            else:
                print("Failed to update expert or policy prevented update.")
                return None
        except Exception as e:
            print(f"Error updating expert: {str(e)}")
            return None

    def delete_expert(self, expert_id: str) -> bool:
        try:
            response = self.supabase.delete_from_table(
                "experts", [("id", "eq", expert_id)]
            )
            if response:
                print("Expert deleted successfully.")
                return True
            else:
                print("Failed to delete expert or policy prevented delete.")
                return False
        except Exception as e:
            print(f"Error deleting expert: {str(e)}")
            return False

    def do_crud_test(self):
        # Create an expert
        new_expert = {
            "id": "34acaa61-7fb4-4c02-b463-a55128e354f3",  # Naviaux
            "expert_name": "Naviaux",
            "full_name": "Bob Naviaux",
            "starting_ref_id": 456,
            "expertise_area": "Machine Learning",
            "experience_years": 10,
            "user_id": "34acaa61-7fb4-4c02-b463-a55128e354f3",
        }

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

        test_add = self.add_expert(test_add, additional_fields)
        print(f"Test add: {test_add}")

        # Read the expert
        expert_name = new_expert["expert_name"]
        optional_fields = ["expertise_area", "experience_years", "bio"]
        expert_data = self.get_expert_plus_by_name(expert_name, optional_fields)
        if expert_data:
            print(f"Expert data: from get_expert_plus_by_name: {expert_data}")
        else:
            print("Read operation failed.")

        # # Update the expert
        expert_id = new_expert["id"]
        update_data = {"experience_years": 11}
        update_success = self.update_expert(expert_id, update_data)
        if update_success:
            print(f"Update operation successful. Updated data: {update_success}")
        else:
            print("Update operation failed.")

        expert_id = new_expert["id"]
        expert_data = self.get_expert_by_id(expert_id)
        print(f"Expert data: from get_expert_by_id: {expert_data}")

        # # Delete the expert
        # delete_success = self.delete_expert(expert_id)
        # if delete_success:
        #     print("Delete operation successful.")
        # else:
        #     print("Delete operation failed.")


def test_crud_operations():
    # Initialize  load_dotenv()
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)
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
