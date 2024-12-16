import streamlit as st
from supabase import create_client
from pathlib import Path


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


def main():
    st.set_page_config(
        page_title="DHG Source Viewer",
        page_icon="📁",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Add custom CSS
    st.markdown(
        """
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
    page = st.sidebar.radio("Go to", ["Supabase Management", "Privacy Policy", "Terms of Service"])

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