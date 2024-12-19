import streamlit as st
from pathlib import Path
from src.core.services.google_pydrive2 import GooglePyDrive2
from src.core.services.supabase_client import SupabaseService


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

    # Initialize SupabaseClient
    api_key = st.secrets["SUPABASE_KEY"]
    url_key = st.secrets["SUPABASE_URL"]
    supabase_client = SupabaseService(url_key, api_key)
    supabase_client.initialize_client()
    users = supabase_client.get_test_users()
    st.write(f"Number of users: {len(users)}")

    show_first_mp4_video()


def show_first_mp4_video():
    # Initialize GooglePyDrive2
    drive_client = GooglePyDrive2()

    try:
        file_list = drive_client.list_files(mime_type="video/mp4")

        if file_list:
            first_mp4 = file_list[0]
            st.write(f"Title: {first_mp4['title']}")

            file_id = first_mp4["id"]
            stream_link = f"https://drive.google.com/file/d/{file_id}/preview"

            st.markdown(
                f'<iframe src="{stream_link}" width="640" height="360"></iframe>',
                unsafe_allow_html=True,
            )
        else:
            st.write("No mp4 files found.")

    except Exception as e:
        st.error(f"Error retrieving mp4 files: {e}")


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

# streamlit run /Users/raybunnage/Documents/github/dhg-source-viewer/streamlit_app.py
