import streamlit as st
from pathlib import Path
import sys
import pandas as pd

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
from src.services.supabase_service import SupabaseService
from src.db.experts import Experts


@st.cache_resource
def get_experts_service():
    """Initialize SupabaseService and Experts as a cached resource"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = SupabaseService(url, key)
    email = st.secrets["TEST_EMAIL"]
    password = st.secrets["TEST_PASSWORD"]
    supabase.login(email, password)
    return Experts(supabase)


def st_manage_experts(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    # Get cached experts service
    experts = get_experts_service()

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
            expertise_area = st.text_input("Expertise Area")
            years_experience = st.number_input(
                "Years of Experience", min_value=0, max_value=100, step=1
            )
            is_in_core_group = st.checkbox("Is in Core Group", value=False)
            if st.button("Add Expert"):
                additional_fields = {
                    "bio": bio,
                    "expertise_area": expertise_area,
                    "experience_years": years_experience,
                    "is_in_core_group": is_in_core_group,
                }
                result = experts.add_expert(
                    expert_name,
                    full_name,
                    email_address,
                    additional_fields,
                )
                if result:
                    st.success(f"Expert '{expert_name}' added successfully")
                else:
                    st.error(f"Failed to add expert for {expert_name}")

        elif action == "Edit":
            st.subheader("Edit Expert")
            additional_fields = ["bio", "expertise_area", "experience_years"]
            experts_list = experts.get_all_experts()
            if not experts_list:
                st.warning("No experts found in the database")
                return

            expert_options = sorted(
                [
                    (
                        expert["id"],
                        expert["expert_name"],
                        expert.get("bio", ""),
                        expert.get("expertise_area", ""),
                        expert.get("experience_years", 0),
                        expert.get("is_in_core_group", False),
                    )
                    for expert in experts_list
                ],
                key=lambda x: x[1],
            )
            selected_expert = st.selectbox(
                "Select Expert to Edit",
                expert_options,
                format_func=lambda x: x[1],
                key="select_expert_to_edit",
            )
            if selected_expert:
                # st.write("Debug - selected_expert tuple:", selected_expert)

                selected_expert_id = selected_expert[0]
                selected_expert_name = selected_expert[1]
                selected_expert_bio = selected_expert[2]
                selected_expert_expertise = selected_expert[3]
                selected_expert_years = selected_expert[4]
                selected_expert_core_group = selected_expert[5]

                full_name = st.text_input("Full Name", value=selected_expert[1])
                bio = st.text_area("Bio", value=selected_expert_bio)
                expertise_area = st.text_input(
                    "Expertise", value=selected_expert_expertise
                )
                experience_years = st.number_input(
                    "Years of Experience",
                    min_value=0,
                    max_value=100,
                    step=1,
                    value=selected_expert_years,
                )
                is_in_core_group = st.checkbox(
                    "Is in Core Group", value=selected_expert_core_group
                )
                if st.button("Update Expert"):
                    update_expert = {
                        "full_name": full_name,
                        "bio": bio,
                        "expertise_area": expertise_area,
                        "experience_years": experience_years,
                        "is_in_core_group": is_in_core_group,
                    }
                    expert = experts.update_expert(selected_expert_id, update_expert)
                    if expert:
                        st.success(
                            f"Expert updated successfully for {selected_expert_name}"
                        )
                    else:
                        st.error(f"Failed to update expert for {selected_expert_name}")

        elif action == "Delete":
            st.subheader("Delete Expert")
            experts_delete = experts.get_all_experts()
            expert_deletes = sorted(
                [(expert["id"], expert["expert_name"]) for expert in experts_delete],
                key=lambda x: x[1],
            )
            selected_expert_id, selected_expert_name = st.selectbox(
                "Select Expert to Delete",
                expert_deletes,
                format_func=lambda x: x[1],
                key="select_expert_to_delete",
            )
            if selected_expert_name:
                if st.button("Delete Expert"):
                    result = experts.delete_expert(selected_expert_id)
                    if result is True:
                        st.success(
                            f"Expert '{selected_expert_name}' deleted successfully"
                        )
                        st.rerun()  # Updated from st.experimental_rerun()
                    else:
                        st.error(f"Failed to delete expert '{selected_expert_name}'")

    with col2:
        st.subheader("All Experts")
        additional_fields = ["bio", "expertise_area", "experience_years"]
        experts_list = experts.get_all_experts(additional_fields)
        if experts_list:
            # Remove 'id' and 'user_id' from each expert dictionary
            for expert in experts_list:
                expert.pop("id", None)
                expert.pop("user_id", None)
            st.dataframe(experts_list, width=1000, height=600)
        else:
            st.warning("No experts found in the database")


# 7c119aee-33f1-438a-b81f-f3d4bb066e8b
if __name__ == "__main__":
    st_manage_experts()

# streamlit run st_shared/st_experts.py