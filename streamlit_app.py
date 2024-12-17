import streamlit as st
from supabase import create_client
from pathlib import Path
from google.oauth2 import service_account
import json
from googleapiclient.discovery import build

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

    


def get_google_credentials_from_secrets():
    google_creds = st.secrets["GOOGLE_CREDENTIALS"]
    try:
        service_account_info = json.loads(google_creds)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        return credentials
    except json.JSONDecodeError:
        st.error("Invalid JSON in GOOGLE_CREDENTIALS secret")
        return None

def get_drive_service_from_secrets():
    credentials = get_google_credentials_from_secrets()
    if credentials:
        return build("drive", "v3", credentials=credentials)
    else:
        st.error("Failed to authenticate with Google Drive")
        return None



def main():
    st.set_page_config(
        page_title="DHG Source Viewer",
        page_icon="📁",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    get_google_credentials_from_secrets()
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
