import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
import json
from googleapiclient.discovery import build

# from pydrive2.auth import GoogleAuth
# from pydrive2.drive import GoogleDrive


# # Improve error handling for dotenv and environment variables
# try:
#     load_dotenv()
#     SUPABASE_URL = os.getenv("SUPABASE_URL")
#     SUPABASE_KEY = os.getenv("SUPABASE_KEY")

#     if not SUPABASE_URL or not SUPABASE_KEY:
#         raise ValueError("Missing required environment variables")

#     supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# except Exception as e:
#     st.error(f"Configuration error: {e}")
#     supabase = None


def get_new_drive_service_from_file():
    credentials = service_account.Credentials.from_service_account_file(
        "client_secrets.json", scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)


def list_new_folders(parent_folder_id=None):
    """List all folders in Google Drive or within a specific folder"""
    service = get_new_drive_service_from_file()

    # Query to search for folders
    query = "mimeType = 'application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    # Add debugging information
    print(f"Using query: {query}")

    # Get folder list
    results = (
        service.files()
        .list(
            q=query,
            fields="files(id, name, webViewLink)",
            pageSize=10,  # Start with a small number to test
        )
        .execute()
    )

    # Print raw results for debugging
    print("Raw API response:", results)

    folders = []
    for file in results.get("files", []):
        folders.append(
            {"id": file["id"], "title": file["name"], "link": file["webViewLink"]}
        )

    return folders


def print_google_credentials():
    # Read your client_secrets.json
    with open("client_secrets.json", "r") as f:
        creds = json.load(f)

    # Convert to single-line string with escaped quotes
    creds_str = json.dumps(creds).replace('"', '\\"')

    # Print the formatted secret
    print(f'GOOGLE_CREDENTIALS = "{creds_str}"')


if __name__ == "__main__":
    list_new_folders()


# def get_drive_service():
#     """Initialize and return Google Drive service"""
#     # Initialize GoogleAuth
#     gauth = GoogleAuth()

#     # Use service account credentials
#     scope = ['https://www.googleapis.com/auth/drive']
#     gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
#         'path/to/your/service-account-file.json',
#         scope
#     )

#     # Create GoogleDrive instance
#     drive = GoogleDrive(gauth)
#     return drive


# def authenticate_user():
#     """Handle user authentication"""
#     if "authenticated" not in st.session_state:
#         st.session_state.authenticated = False

#     if not st.session_state.authenticated:
#         # Add check for Supabase client
#         if not supabase:
#             st.error("Unable to connect to authentication service")
#             return False

#         with st.form("login_form"):
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             submit = st.form_submit_button("Login")

#             if submit:
#                 try:
#                     response = supabase.auth.sign_in_with_password(
#                         {"email": email, "password": password}
#                     )
#                     st.session_state.authenticated = True
#                     st.session_state.user = response.user
#                     return True
#                 except Exception as e:
#                     st.error("Invalid credentials")
#                     return False
#         return False
#     return True


# # Approach 1: Using JSON file (good for local development)
# def get_drive_service_from_file():
#     # Create credentials using service_account
#     credentials = service_account.Credentials.from_service_account_file(
#         "client_secrets.json", scopes=["https://www.googleapis.com/auth/drive"]
#     )

#     # Initialize GoogleAuth
#     gauth = GoogleAuth()
#     # Set credentials directly
#     gauth.credentials = credentials

#     # Create and return GoogleDrive instance with auth
#     drive = GoogleDrive(gauth)
#     return drive


# def print_folders():
#     folders = list_folders()
#     for folder in folders:
#         print(f"Folder: {folder['title']}, ID: {folder['id']}")


# def list_folders(parent_folder_id=None):
#     """List all folders in Google Drive or within a specific folder"""
#     drive = get_drive_service_from_file()

#     # Query to search for folders
#     query = "mimeType = 'application/vnd.google-apps.folder'"
#     if parent_folder_id:
#         query += f" and '{parent_folder_id}' in parents"

#     # Get folder list
#     file_list = drive.ListFile({"q": query}).GetList()

#     folders = []
#     for file in file_list:
#         folders.append(
#             {"id": file["id"], "title": file["title"], "link": file["alternateLink"]}
#         )

#     return folders


# # Approach 2: Using environment variable (good for deployment)
# def get_credentials_from_env():
#     google_creds = os.getenv("GOOGLE_CREDENTIALS")
#     if not google_creds:
#         raise ValueError("GOOGLE_CREDENTIALS environment variable is not set")

#     try:
#         service_account_info = json.loads(google_creds)
#         credentials = service_account.Credentials.from_service_account_info(
#             service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
#         )
#         return credentials
#     except json.JSONDecodeError:
#         raise ValueError(
#             "GOOGLE_CREDENTIALS environment variable contains invalid JSON"
#         )


# def get_google_credentials():
#     """Create Google service account credentials"""
#     credentials = service_account.Credentials.from_service_account_file(
#         'path/to/your/service-account-file.json',
#         scopes=['https://www.googleapis.com/auth/spreadsheets',  # adjust scopes based on your needs
#                 'https://www.googleapis.com/auth/drive']
#     )
#     return credentials


# def get_google_credentials2():
#     """Create Google service account credentials from environment variable"""
#     service_account_info = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
#     credentials = service_account.Credentials.from_service_account_info(
#         service_account_info,
#         scopes=['https://www.googleapis.com/auth/spreadsheets',
#                 'https://www.googleapis.com/auth/drive']
#     )
#     return credentials


load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def authenticate_user():
    """Handle user authentication"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                try:
                    response = supabase.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    st.session_state.authenticated = True
                    st.session_state.user = response.user
                    return True
                except Exception as e:
                    st.error("Invalid credentials")
                    return False
        return False
    return True
