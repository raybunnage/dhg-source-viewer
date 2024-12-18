import streamlit as st
from supabase import create_client
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
# from pydrive2.auth import GoogleAuth
# from pydrive2.drive import GoogleDrive
# from oauth2client.service_account import ServiceAccountCredentials


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


def main():
    st.set_page_config(
        page_title="DHG Source Viewer",
        page_icon="📁",
        layout="wide",
        initial_sidebar_state="expanded",
    )

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
