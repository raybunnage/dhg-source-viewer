import streamlit as st

# Set page config before any other Streamlit commands
st.set_page_config(layout="wide")

import pandas as pd
from pathlib import Path
import sys
from typing import Dict, List, Set
from collections import defaultdict

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
from st_shared.streamlit_base import StreamlitBase
from src.services.supabase_service import SupabaseService
from src.db.experts import Experts


class AsyncExpertsConnection:
    def __init__(self):
        self.client = None
        self._initialized = False

    async def initialize(self):
        """Initialize the Supabase connection"""
        if not self._initialized:
            try:
                url = st.secrets["SUPABASE_URL"]
                key = st.secrets["SUPABASE_KEY"]
                supabase = SupabaseService(url, key)
                email = st.secrets["TEST_EMAIL"]
                password = st.secrets["TEST_PASSWORD"]

                await supabase.login(email, password)
                self.client = Experts(supabase)
                self._initialized = True
                st.session_state.app_state.is_initialized = True
            except Exception as e:
                raise Exception(f"Failed to initialize Supabase connection: {e}")

    async def get_client(self):
        """Get the initialized client, initializing if necessary"""
        if not self._initialized:
            await self.initialize()
        return self.client


class ExpertsManager(StreamlitBase):
    def __init__(self):
        super().__init__("experts_manager")
        self.connection = self._get_connection()

    @staticmethod
    @st.cache_resource
    def _get_connection():
        """Cache the connection instance"""
        return AsyncExpertsConnection()

    def _validate_data(self, data):
        """Implement the abstract method from BaseDB"""
        # Basic validation - check if data is a dict and not empty
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        if not data:
            raise ValueError("Data cannot be empty")
        return True

    async def add_expert(self, expert_data: dict):
        """Add a new expert"""
        try:
            client = await self.connection.get_client()
            result = await client.add(
                expert_data["expert_name"],
                expert_data["full_name"],
                expert_data["email_address"],
                {
                    "bio": expert_data["bio"],
                    "expertise_area": expert_data["expertise_area"],
                    "experience_years": expert_data["experience_years"],
                    "is_in_core_group": expert_data["is_in_core_group"],
                },
            )
            if result:
                self.logger.info(
                    f"Successfully added expert: {expert_data['expert_name']}"
                )
                return True
            return False
        except Exception as e:
            self.set_error(f"Error adding expert: {str(e)}")
            return False

    async def update_expert(self, expert_id: str, expert_data: dict):
        """Update an existing expert"""
        try:
            client = await self.connection.get_client()
            result = await client.update(expert_id, expert_data)
            if result:
                self.logger.info(f"Successfully updated expert ID: {expert_id}")
                return True
            return False
        except Exception as e:
            self.set_error(f"Error updating expert: {str(e)}")
            return False

    async def delete_expert(self, expert_id: str):
        """Delete an expert permanently"""
        try:
            client = await self.connection.get_client()
            result = await client.delete(expert_id)  # This now performs a hard delete
            if result:
                self.logger.info(f"Successfully deleted expert ID: {expert_id}")
                return True
            return False
        except Exception as e:
            self.set_error(f"Error deleting expert: {str(e)}")
            return False

    async def get_all_experts(self, additional_fields: List[str] = None):
        """Get all experts"""
        try:
            client = await self.connection.get_client()
            experts_list = await client.get_all(additional_fields)
            return experts_list
        except Exception as e:
            self.set_error(f"Error fetching experts: {str(e)}")
            return []

    async def get_aliases(self, expert_name: str):
        """Get aliases for an expert"""
        try:
            client = await self.connection.get_client()
            aliases = await client.get_alias(expert_name)
            return aliases
        except Exception as e:
            self.set_error(f"Error fetching aliases: {str(e)}")
            return []

    async def add_alias(self, expert_name: str, alias_name: str):
        """Add an alias for an expert"""
        try:
            client = await self.connection.get_client()
            result = await client.add_alias(expert_name, alias_name)
            if result:
                self.logger.info(
                    f"Successfully added alias '{alias_name}' for {expert_name}"
                )
            return result
        except Exception as e:
            self.set_error(f"Error adding alias: {str(e)}")
            return False

    async def delete_alias(self, alias_id: int):
        """Delete an alias"""
        try:
            client = await self.connection.get_client()
            result = await client.delete_alias(alias_id)
            if result:
                self.logger.info(f"Successfully deleted alias ID: {alias_id}")
            return result
        except Exception as e:
            self.set_error(f"Error deleting alias: {str(e)}")
            return False

    def render_add_expert_form(self):
        """Render the add expert form"""
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
            expert_data = {
                "expert_name": expert_name,
                "full_name": full_name,
                "email_address": email_address,
                "bio": bio,
                "expertise_area": expertise_area,
                "experience_years": years_experience,
                "is_in_core_group": is_in_core_group,
            }
            if self.run_async(self.add_expert(expert_data)):
                st.success(f"Expert '{expert_name}' added successfully")
                st.rerun()

    def render_edit_expert_form(self):
        """Render the edit expert form"""
        st.subheader("Edit Expert")
        experts_list = self.run_async(
            self.get_all_experts(["bio", "expertise_area", "experience_years"])
        )

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
                    expert.get("email_address", ""),
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
            selected_expert_id = selected_expert[0]
            selected_expert_name = selected_expert[1]
            full_name = st.text_input("Full Name", value=selected_expert[1])
            bio = st.text_area("Bio", value=selected_expert[2])
            expertise_area = st.text_input("Expertise", value=selected_expert[3])
            email_address = st.text_input("Email Address", value=selected_expert[6])
            experience_years = st.number_input(
                "Years of Experience",
                min_value=0,
                max_value=100,
                step=1,
                value=selected_expert[4],
            )
            is_in_core_group = st.checkbox("Is in Core Group", value=selected_expert[5])

            if st.button("Update Expert"):
                update_expert = {
                    "full_name": full_name,
                    "bio": bio,
                    "expertise_area": expertise_area,
                    "experience_years": experience_years,
                    "is_in_core_group": is_in_core_group,
                    "email_address": email_address,
                }
                if self.run_async(
                    self.update_expert(selected_expert_id, update_expert)
                ):
                    st.success(
                        f"Expert updated successfully for {selected_expert_name}"
                    )
                    st.rerun()

    def render_delete_expert_form(self):
        """Render the delete expert form"""
        st.subheader("Delete Expert")
        experts_list = self.run_async(self.get_all_experts())

        expert_deletes = sorted(
            [(expert["id"], expert["expert_name"]) for expert in experts_list],
            key=lambda x: x[1],
        )

        selected_expert = st.selectbox(
            "Select Expert to Delete",
            expert_deletes,
            format_func=lambda x: x[1],
            key="select_expert_to_delete",
        )

        if selected_expert:
            selected_expert_id, selected_expert_name = selected_expert
            if st.button("Delete Expert"):
                # Add a confirmation check before deletion
                if st.checkbox("I understand this action cannot be undone"):
                    self.logger.info(
                        f"Attempting to delete expert: {selected_expert_name}"
                    )
                    if self.run_async(self.delete_expert(selected_expert_id)):
                        st.success(
                            f"Expert '{selected_expert_name}' deleted successfully"
                        )
                        st.rerun()
                else:
                    st.warning("Please confirm the permanent deletion")

    def render_alias_form(self):
        """Render the alias management form"""
        st.subheader("Alias Expert")
        experts_list = self.run_async(self.get_all_experts())

        expert_aliases = sorted(
            [(expert["id"], expert["expert_name"]) for expert in experts_list],
            key=lambda x: x[1],
        )

        selected_expert = st.selectbox(
            "Select Expert",
            expert_aliases,
            format_func=lambda x: x[1],
            key="select_expert_to_alias",
        )

        if selected_expert:
            selected_expert_id, selected_expert_name = selected_expert
            alias_name = st.text_input("Alias Name")

            if alias_name and st.button("Add Alias"):
                if self.run_async(self.add_alias(selected_expert_name, alias_name)):
                    st.success(f"Alias '{alias_name}' added successfully")
                    st.rerun()

            # Display existing aliases
            aliases = self.run_async(self.get_aliases(selected_expert_name))
            if aliases:
                st.subheader(f"Aliases for {selected_expert_name}")
                df = pd.DataFrame(aliases)
                df = df[["id", "alias_name"]]
                st.dataframe(
                    df,
                    hide_index=True,
                    column_config={"alias_name": st.column_config.Column(width=300)},
                )

                alias_id_to_delete = st.number_input(
                    "Enter Alias ID to Delete", min_value=0, step=1
                )
                if alias_id_to_delete and st.button("Delete Alias"):
                    if self.run_async(self.delete_alias(alias_id_to_delete)):
                        st.success(
                            f"Alias with ID '{alias_id_to_delete}' deleted successfully"
                        )
                        st.rerun()
            else:
                st.warning(f"No aliases found for {selected_expert_name}")

    def main(self, set_page_config: bool = False):
        # Initialize connection
        if not st.session_state.app_state.is_initialized:
            try:
                self.run_async(self.connection.initialize())
            except Exception as e:
                self.set_error(str(e))

        # Show any errors
        self.show_error()

        # Create two columns
        col1, col2 = st.columns(2)

        with col1:
            st.sidebar.title("Manage Experts")
            st.sidebar.subheader("Actions")
            action = st.sidebar.radio(
                "Select Action", ["Add", "Edit", "Delete", "Alias"]
            )

            if action == "Add":
                self.render_add_expert_form()
            elif action == "Edit":
                self.render_edit_expert_form()
            elif action == "Delete":
                self.render_delete_expert_form()
            elif action == "Alias":
                self.render_alias_form()

        with col2:
            st.subheader("All Experts")
            experts_list = self.run_async(
                self.get_all_experts(["bio", "expertise_area", "experience_years"])
            )
            if experts_list:
                # Remove 'id' and 'user_id' from each expert dictionary
                for expert in experts_list:
                    expert.pop("id", None)
                    expert.pop("user_id", None)
                st.dataframe(experts_list, width=1000, height=600)
            else:
                st.warning("No experts found in the database")


if __name__ == "__main__":
    app = ExpertsManager()
    app.main()

# streamlit run st_shared/st_experts.py
