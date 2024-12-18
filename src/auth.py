import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials


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


def do_load_dotenv():
    load_dotenv()
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
    print(GOOGLE_CREDENTIALS)


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

    # Approach 2: Using environment variable (good for deployment)


def get_credentials_from_env():
    google_creds = os.getenv("GOOGLE_CREDENTIALS")
    if not google_creds:
        raise ValueError("GOOGLE_CREDENTIALS environment variable is not set")

    try:
        service_account_info = json.loads(google_creds)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        return credentials
    except json.JSONDecodeError:
        raise ValueError(
            "GOOGLE_CREDENTIALS environment variable contains invalid JSON"
        )


def print_google_credentials():
    # Read your client_secrets.json
    with open("client_secrets.json", "r") as f:
        creds = json.load(f)

    # Convert to single-line string with escaped quotes
    creds_str = json.dumps(creds).replace('"', '\\"')

    # Print the formatted secret
    print(f'GOOGLE_CREDENTIALS = "{creds_str}"')


def get_google_credentials_from_secrets():
    try:
        google_creds = st.secrets["GOOGLE_CREDENTIALS"]

        # If the credentials are already a dict, use them directly
        if isinstance(google_creds, dict):
            service_account_info = google_creds
        else:
            # Clean up the credentials string
            if isinstance(google_creds, str):
                # Remove any extra quotes and whitespace
                google_creds = google_creds.strip().strip("\"'")

                # Handle the private key newlines before JSON parsing
                google_creds = google_creds.replace(
                    "\\n", "\\\\n"
                )  # Double escape newlines
                google_creds = google_creds.replace(
                    "\n", "\\n"
                )  # Handle actual newlines

                try:
                    service_account_info = json.loads(google_creds)
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error at position {e.pos}: {e.msg}")
                    print(
                        f"Context: ...{google_creds[max(0, e.pos-50):min(len(google_creds), e.pos+50)]}..."
                    )
                    return None
            else:
                print(f"Unexpected credentials type: {type(google_creds)}")
                return None

        # Fix private key formatting after parsing
        if "private_key" in service_account_info:
            service_account_info["private_key"] = service_account_info[
                "private_key"
            ].replace("\\n", "\n")

        # Rest of the function remains the same...
        required_fields = [
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
        ]
        missing_fields = [
            field for field in required_fields if field not in service_account_info
        ]
        if missing_fields:
            print(f"Missing required fields in credentials: {missing_fields}")
            return None

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        return credentials

    except Exception as e:
        print(f"Unexpected error in get_google_credentials_from_secrets: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


# rom google.oauth2 import service_account

# The private key from Google should be formatted with literal \n characters
# replaced with actual newlines and proper begin/end markers


def format_service_account_key(private_key):
    """
    Format a service account configuration with proper private key formatting.

    Args:
        client_id (str): The client ID from Google
        private_key (str): The private key string from the JSON credentials

    Returns:
        dict: Properly formatted service account info dictionary
    """
    # Ensure the private key has proper newlines
    formatted_key = private_key.replace("\\n", "\n")

    # Make sure the key has proper BEGIN/END markers if they're missing
    if not formatted_key.startswith("-----BEGIN PRIVATE KEY-----"):
        formatted_key = "-----BEGIN PRIVATE KEY-----\n" + formatted_key
    if not formatted_key.endswith("-----END PRIVATE KEY-----"):
        formatted_key = formatted_key + "\n-----END PRIVATE KEY-----\n"

    # Create the service account info dictionary
    service_account_info = {
        "type": "service_account",
        "project_id": "fabled-imagery-444902-k1",
        "private_key": formatted_key,
        "private_key_id": st.secrets["PRIVATE_KEY_ID"],
        "client_email": st.secrets["CLIENT_EMAIL"],
        "client_id": st.secrets["CLIENT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dhg-drive-helper%40fabled-imagery-444902-k1.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }

    return service_account_info


# Example usage:


def get_test_drive_service():
    private_key = st.secrets["PRIVATE_KEY"]
    try:
        service_account_info = format_service_account_key(private_key)

        # Create credentials using the formatted info
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/drive"],
        )

    except ValueError as e:
        print(f"Error creating credentials: {e}")

    return build("drive", "v3", credentials=credentials)


def get_pydrive_test_drive_service():
    private_key = st.secrets["PRIVATE_KEY"]
    try:
        service_account_info = format_service_account_key(private_key)

        # Create a GoogleAuth instance
        gauth = GoogleAuth()

        # Use service account credentials
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
        )

        # Create GoogleDrive instance
        drive = GoogleDrive(gauth)
        return drive

    except ValueError as e:
        print(f"Error creating credentials: {e}")
        return None


def test_pydrive_service_account():
    """Test if PyDrive2 is associated with the service account and return a list of folders"""
    drive = get_pydrive_test_drive_service()
    if not drive:
        print("Failed to authenticate with PyDrive")
        return []

    try:
        # Update the query to match the working Google API query
        file_list = drive.ListFile(
            {
                "q": "mimeType='application/vnd.google-apps.folder'"  # Remove the 'root' in parents restriction
            }
        ).GetList()

        folders = []
        if file_list:
            print("Successfully authenticated with PyDrive using the service account.")
            print(f"Found {len(file_list)} folders:")
            for file in file_list:
                folder_info = {"title": file["title"], "id": file["id"]}
                print(f"- {folder_info['title']} (ID: {folder_info['id']})")
                folders.append(folder_info)
        else:
            print("Authenticated but no folders found.")

        return folders

    except Exception as e:
        print(f"Error verifying PyDrive service account association: {e}")
        return []


def test_drive_and_folders():
    """Test the list_new_folders function"""
    try:
        folders = test_list_new_folders()
        if not folders:
            print("No folders found.")
        else:
            print("Folders found:")
            for folder in folders:
                print(
                    f"ID: {folder['id']}, Title: {folder['title']}, Link: {folder['link']}"
                )
    except Exception as e:
        print(f"Error during test: {e}")


def test_list_new_folders(parent_folder_id=None):
    """List all folders in Google Drive or within a specific folder"""
    service = get_test_drive_service()

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


if __name__ == "__main__":
    test_pydrive_service_account()
    # test_list_new_folders()
    # print_google_credentials()
    # do_load_dotenv()
    # print_google_credentials()


# load_dotenv()

# supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


# def authenticate_user():
#     """Handle user authentication"""
#     if "authenticated" not in st.session_state:
#         st.session_state.authenticated = False

#     if not st.session_state.authenticated:
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


# def get_root_folder():
#     drive = get_pydrive_test_drive_service()
#     if not drive:
#         print("Failed to get drive service")
#         return None

#     # Get the root folder by querying for 'root' in parents
#     root_folder = drive.ListFile({"q": "'root' in parents"}).GetList()

#     # Print contents for debugging
#     for file in root_folder:
#         print(f"Found: {file['title']} (ID: {file['id']}, Type: {file['mimeType']})")

#     return root_folder
