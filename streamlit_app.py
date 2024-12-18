import streamlit as st
from supabase import create_client
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials


def show_privacy_policy():
    privacy_policy_path = Path(__file__).parent / "docs" / "privacy-policy.md"
    with open(privacy_policy_path, "r") as f:
        privacy_policy_content = f.read()
    st.markdown(privacy_policy_content)


def show_terms_of_service():
    terms_path = Path(__file__).parent / "docs" / "terms-of-service.md"
    with open(terms_path, "r") as f:
        terms_content = f.read()
    st.markdown(terms_content)


def show_supabase_management():
    st.title("Supabase Connection Test")

    api_key = st.secrets["SUPABASE_KEY"]
    url_key = st.secrets["SUPABASE_URL"]

    supabase = create_client(url_key, api_key)

    users = supabase.table("test").select("*").execute()
    st.write(f"Number of users: {len(users.data)}")

    test_pydrive_service_account()
    # test_list_new_folders()


def test_list_new_folders(parent_folder_id=None):
    """List all folders in Google Drive or within a specific folder"""
    service = get_test_drive_service()

    # Query to search for folders
    query = "mimeType = 'application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    # Add debugging information
    st.write(f"Using query: {query}")

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
    st.write("Raw API response:", results)

    folders = []
    for file in results.get("files", []):
        folders.append(
            {"id": file["id"], "title": file["name"], "link": file["webViewLink"]}
        )

    return folders


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
        st.error(f"Error creating credentials: {e}")

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
    """Test if PyDrive2 is associated with the service account"""
    drive = get_pydrive_test_drive_service()
    if not drive:
        print("Failed to authenticate with PyDrive")
        return False

    try:
        # Update the query to match the working Google API query
        file_list = drive.ListFile(
            {
                "q": "mimeType='application/vnd.google-apps.folder'"  # Remove the 'root' in parents restriction
            }
        ).GetList()

        if file_list:
            print("Successfully authenticated with PyDrive using the service account.")
            print(f"Found {len(file_list)} folders:")
            for file in file_list:
                print(f"- {file['title']} (ID: {file['id']})")
            return True
        else:
            print("Authenticated but no folders found.")
            return True

    except Exception as e:
        print(f"Error verifying PyDrive service account association: {e}")
        return False

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


def main():
    st.set_page_config(
        page_title="DHG Source Viewer",
        page_icon="📁",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # st.title("Secrets Management")

    # st.write("Here are the secrets available in the app:")

    # for key, value in st.secrets.items():
    #     st.write(f"{key}: {value}")

    # Add custom CSS and meta tag
    st.markdown(
        """
        <head>
            <meta name="google-site-verification" content="uWwZGPEj-VhyxnZR6ZY30cLk_HiL-PVPYyBz0M1w36I" />
        </head>
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Navigation sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to", ["Supabase Management", "Privacy Policy", "Terms of Service"]
    )

    # Display the selected page
    if page == "Supabase Management":
        show_supabase_management()
    elif page == "Privacy Policy":
        show_privacy_policy()
    elif page == "Terms of Service":
        show_terms_of_service()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 10px;">
            © 2024 DHG Source Viewer. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

# streamlit run streamlit_app.py
