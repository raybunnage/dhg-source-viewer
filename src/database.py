from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# os.environ["SUPABASE_URL"] = "https://jdksnfkupzywjdfefkyj.supabase.co"
# os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impka3NuZ$"

# print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
# print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))

# https://jdksnfkupzywjdfefkyj.supabase.co


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impka3NuZmt1cHp5d2pkZmVma3lqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQxODkwMTMsImV4cCI6MjA0OTc2NTAxM30.035475oKIiE1pSsfQbRoje4-FRT9XDKAk6ScHYtaPsQ


def test_supabase_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in environment variables")

    supabase: Client = create_client(url, key)

    # Test fetching data from a sample table
    response = supabase.table("test").select("*").execute()
    print(response)  # this is the response from the supabase table
    return response


if __name__ == "__main__":
    response = test_supabase_connection()
    print(response)


# supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


# def get_folders():

#     """Fetch available folders from Supabase"""
#     try:
#         response = supabase.table('folders').select("*").execute()
#         return [folder['name'] for folder in response.data]
#     except Exception as e:
#         print(f"Error fetching folders: {e}")
#         return []

# def get_files(folder_name):
#     """Fetch files for a specific folder from Supabase"""
#     try:
#         response = supabase.table('files')\ #             .select("*")\
#             .eq('folder_name', folder_name)\
#             .execute()
#         return response.data #     except Exception as e: #         print(f"Error fetching files: {e}")
#         return []


# print(get_folders())
# print(get_files("test"))
