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
        "private_key_id": "4abf1e79183be159f2a02ebdf2079440cee5b23d",
        "client_email": "dhg-drive-helper@fabled-imagery-444902-k1.iam.gserviceaccount.com",
        "client_id": "112125686334929012732",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dhg-drive-helper%40fabled-imagery-444902-k1.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }

    return service_account_info


# Example usage:

private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCxFksSsliR5nfB\nU4zvFpiMA2yepgsDmMEDPvk/PzizIEYcti9C9oPAJbCUjCFzAebcYULN35bstsOw\nK4Zo4M1YxQJhOdBWWrEcnRjjgz0oUV7/xN0Y7s69yPJ4c4Brz64Rdz14DVjNxFxx\nGAsJZZWcMdHnWEDGCnB7DhNbeoTgOcnbM/HvfJLjboTTT0BtGvUoaIfyMGxUVqox\nzez0aRioaZhFgoIjwvTsergi9kRlR9c4kkh0hKDOjvvzSsvLZeGICkM+VSKK+OZa\nYNHJwmYaZyfwz6A8cyvfPJtyeuUpR38bfBn+enm4ncpjd9VT70EHHTY/SqNGX0Fu\nIMYz/28XAgMBAAECggEAP9tyoeDXCHGrkHbA9PxYcPDRK9pjUV41h6afOXviRdGn\nBrZ5j3OWaeUNalunujGe3qxh6xwr79st8KqZUttxoQeVxpqS8njMsi1CKtSJ6q6B\nC8khE1sWCSDbsqyvy/C9a8XsUAy8D6M11IBfhnlvvD3I29waq29bRTx7pXqmTLZg\ncCdbscHSTwfPCcwNgU7XihkmLUUft94k61oeXD9hf6mbWmY78AqU+H2FzEVsOhLu\n5UCJA+OlBB8+s5ZQRQeThPRE8TfleBotSfKcqg1LLYfFPxMrMJxCjl6Jjk+azIHl\nuxANvuIQntIwIKTlF5WXp42RNfVy82RpvSdPwqJCnQKBgQDWqY4mGO2zcYCaFTCK\nazWGU4v7y+4usR3mJ7ELPnJrrlP4lUocUfo/wY/am/cLT0Hbm6NtnaxKEgHtcdDG\ntr8iNG2cPNQD9nQdF8FYNNe1DjRUJt9qCTnHtHx8egU28mQURlL6ULB0snJU1reF\n4RIC1Lpbntj4RrybQJ6EqmbXnQKBgQDTMFmV5tKvDsRbcBY3CQlZkV9sWJKYwAsP\naC1AtUzYi35x1u3vxjhWPcbnUnp5xGSdw2fRpKrBqsQ9UgZH98dlZ8YIpojRwXul\nClEE4CTPpAGeE80JHK6ldAw/WcRDlUUoIFXb2gJ2aNcMEz9u3P/cdWpecpfzfdzt\nQTfTmT+1QwKBgEcPhBYKhI21kivvvczkpqhb+egV3zgnu80X8JzXREtvPy74RLtR\nS/VVH0jv/n0I9LU9NYGxA3rVsTuoRMOzdVxeXLau0ESrjk6fMYsAmzO9iwccgzL3\n8N+yWM9gGV/SJ90qVoe0tGU9OWnqVoCEPFEhmLuBvzOZPxBp+M/UFQ1lAoGBAKYj\nokZoGRR4lIaujftr03wv/ha5M1KRueG7/eWq+zJbwvSBthtsIAPQg7qVSx6iHtlx\n0Sm+1kqXMdxfu+tABRBEbCmAAaCqCsBSdlxUjQEAr/kQ8LsbYlVtDvmDf//+3THt\nBj53qnpGje7E8aEgoPRpNm3ozptSR8wqA2YmaFULAoGBAIXQ5CE24kOg/hDWceOs\nNv50Chlwgo3Inl3V+/uNRhD5yKhw/zKs3YI47kKj1qIHQRHHFS1g4GTH40n6MhFs\nszneDRkynm4UhFg9z1T81vAisYES8gt/kitQmGjx/ZPWTWbQyNa9EuSTC3JS6mpz\nv9CInTHY342J+dWP28aBaRP3\n-----END PRIVATE KEY-----\n"


def get_test_drive_service():
    try:
        service_account_info = format_service_account_key(private_key)

        # Create credentials using the formatted info
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    except ValueError as e:
        print(f"Error creating credentials: {e}")

    return credentials


if __name__ == "__main__":
    get_test_drive_service()
    # print_google_credentials()
    # do_load_dotenv()
    # print_google_credentials()


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


# load_dotenv()

# supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


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
