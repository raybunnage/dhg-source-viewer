import sys
import streamlit as st
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))
from src.services.supabase_service import SupabaseService
from st_shared.st_login import test_supabase_connection


def show_support_test():
    st.title("Support Test")
    test_supabase_connection()

    # url_key = st.secrets["SUPABASE_URL"]
    # api_key = st.secrets["SUPABASE_KEY"]
    # test_email = st.secrets["TEST_EMAIL"]
    # test_password = st.secrets["TEST_PASSWORD"]
    # # st.write(test_email)
    # # st.write(test_password)
    # supabase_client = SupabaseService(url_key, api_key)
    # supabase_client.login(test_email, test_password)
    # users = supabase_client.get_test_users()
    # todos = supabase_client.get_todos()
    # todos_data = todos.data if hasattr(todos, "data") else []
    # st.write(f"Number of todos: {len(todos_data)}")

    # # st.write(users)
    # # Convert the APIResponse to a list or dict before using len()
    # users_data = users.data if hasattr(users, "data") else []
    # st.write(f"Number of users: {len(users_data)}")


if __name__ == "__main__":
    show_support_test()

# streamlit run apps/extravaganza_support/st_support_test.py
