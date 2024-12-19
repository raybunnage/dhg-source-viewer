import streamlit as st
from pathlib import Path
from src.core.services.google_pydrive2 import GooglePyDrive2
from src.core.services.supabase_client import SupabaseService



# Add the project root to Python path


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

    url_key = st.secrets["SUPABASE_URL"]
    api_key = st.secrets["SUPABASE_KEY"]
    supabase_client = SupabaseService(url_key, api_key)
    supabase_client.initialize_client()
    users = supabase_client.get_test_users()
    # st.write(users)
    # Convert the APIResponse to a list or dict before using len()
    users_data = users.data if hasattr(users, "data") else []
    st.write(f"Number of users: {len(users_data)}")

    show_first_mp4_video()


def show_first_mp4_video():
    private_key = st.secrets["PRIVATE_KEY"]
    private_key_id = st.secrets["PRIVATE_KEY_ID"]
    client_email = st.secrets["CLIENT_EMAIL"]
    client_id = st.secrets["CLIENT_ID"]
    drive = GooglePyDrive2(private_key, private_key_id, client_email, client_id)
    if not drive:
        st.error("Failed to authenticate with PyDrive")
        return

    try:
        # Query to search for mp4 files
        file_list = drive.ListFile()

        if file_list:
            first_mp4 = file_list[0]
            st.write(f"Title: {first_mp4['title']}")

            # Get the file ID and create a direct streaming link
            file_id = first_mp4["id"]
            stream_link = f"https://drive.google.com/file/d/{file_id}/preview"

            # Display using st.markdown with iframe
            st.markdown(
                f'<iframe src="{stream_link}" width="640" height="360"></iframe>',
                unsafe_allow_html=True,
            )
        else:
            st.write("No mp4 files found.")
    except Exception as e:
        st.error(f"Error retrieving mp4 files: {e}")
    finally:
        st.write("Finished processing mp4 files.")


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

# streamlit run src/apps/app1/components/drive_viewer.py