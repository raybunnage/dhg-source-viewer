import streamlit as st
from pathlib import Path
import sys
import pandas as pd

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
from src.services.supabase_service import SupabaseService
from src.db.experts import Experts


def initialize_page():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = SupabaseService(url, key)
    email = st.secrets["TEST_EMAIL"]
    password = st.secrets["TEST_PASSWORD"]
    supabase.login(email, password)
    experts = Experts(supabase)
    return experts
    # expert_service.do_crud_test()


def st_manage_experts(set_page_config: bool = True):
    experts = initialize_page()
    if set_page_config:
        st.set_page_config(layout="wide")

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        st.sidebar.title("Manage Experts")
        st.sidebar.subheader("Actions")
        action = st.sidebar.radio("Select Action", ["Add", "Edit", "Delete"])

        if action == "Add":
            st.subheader("Add Expert")
            expert_name = st.text_input("Expert Name")
            full_name = st.text_input("Full Name")
            email_address = st.text_input("Email Address")
            bio = st.text_area("Bio")
            expertise = st.text_input("Expertise")
            years_experience = st.number_input(
                "Years of Experience", min_value=0, max_value=100, step=1
            )
            if st.button("Add Expert"):

                additional_fields = {
                    "bio": bio,
                    "expertise": expertise,
                    "years_experience": years_experience,
                }
                result = experts.add_expert(
                    expert_name,
                    full_name,
                    email_address,
                    additional_fields,
                )
                if result:
                    st.success("Expert added successfully")
                else:
                    st.error("Failed to add expert")

        # elif action == "Edit":
        #     st.subheader("Edit Expert")
        #     experts = Experts.get_all_experts()
        #     expert_names = sorted([expert.expert_name for expert in experts])
        #     selected_expert_name = st.selectbox("Select Expert to Edit", expert_names)
        #     if selected_expert_name:
        #         selected_expert = next(
        #             expert
        #             for expert in experts
        #             if expert.expert_name == selected_expert_name
        #         )
        #         full_name = st.text_input("Full Name", value=selected_expert.full_name)
        #         bio = st.text_area("Bio", value=selected_expert.bio)
        #         expertise = st.text_input("Expertise", value=selected_expert.expertise)
        #         years_experience = st.number_input(
        #             "Years of Experience",
        #             min_value=0,
        #             max_value=100,
        #             step=1,
        #             value=selected_expert.years_experience,
        #         )
        #         if st.button("Update Expert"):
        #             selected_expert.full_name = full_name
        #             selected_expert.bio = bio
        #             selected_expert.expertise = expertise
        #             selected_expert.years_experience = years_experience
        #             selected_expert.save()
        #             st.success("Expert updated successfully")

        # elif action == "Delete":
        #     st.subheader("Delete Expert")
        #     experts = Experts.get_all()
        #     expert_names = sorted([expert.expert_name for expert in experts])
        #     selected_expert_name = st.selectbox("Select Expert to Delete", expert_names)
        #     if selected_expert_name:
        #         selected_expert = next(
        #             expert
        #             for expert in experts
        #             if expert.expert_name == selected_expert_name
        #         )
        #         if st.button("Delete Expert"):
        #             selected_expert.delete()
        #             st.success("Expert deleted successfully")

    with col2:
        pass
        # st.subheader("All Experts")
        # experts = Experts.get_all_experts()
        # experts_data = [
        #     {
        #         "Expert Name": expert.expert_name,
        #         "Full Name": expert.full_name,
        #         "Email Address": expert.email_address,
        #         "Bio": expert.bio,
        #         "Expertise": expert.expertise,
        #         "Years of Experience": expert.years_experience,
        #     }
        #     for expert in experts
        # ]
        # df = pd.DataFrame(experts_data)
        # st.dataframe(df)


if __name__ == "__main__":
    st_manage_experts()

# streamlit run st_shared/st_experts.py
