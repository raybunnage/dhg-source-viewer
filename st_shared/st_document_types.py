import streamlit as st

st.set_page_config(layout="wide")

from pathlib import Path
import sys
import pandas as pd
from typing import List

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from st_shared.streamlit_base import StreamlitBase
from src.services.supabase_service import SupabaseService
from src.db.uni_document_types import DocumentTypes


class AsyncDocumentTypesConnection:
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
                self.client = DocumentTypes(supabase)
                self._initialized = True
                st.session_state.app_state.is_initialized = True
            except Exception as e:
                raise Exception(f"Failed to initialize Supabase connection: {e}")

    async def get_client(self):
        """Get the initialized client, initializing if necessary"""
        if not self._initialized:
            await self.initialize()
        return self.client


class DocumentTypesManager(StreamlitBase):
    def __init__(self):
        super().__init__("document_types_manager")
        self.connection = self._get_connection()

    @staticmethod
    @st.cache_resource
    def _get_connection():
        """Cache the connection instance"""
        return AsyncDocumentTypesConnection()

    async def add_document_type(self, document_type_data: dict):
        """Add a new document type"""
        try:
            client = await self.connection.get_client()
            result = await client.add(
                document_type_data["document_type"],
                document_type_data["description"],
                document_type_data["mime_type"],
                document_type_data["file_extension"],
                document_type_data["category"],
                document_type_data["is_ai_generated"],
            )
            if result:
                self.logger.info(
                    f"Successfully added document type: {document_type_data['document_type']}"
                )
                return True
            return False
        except Exception as e:
            self.set_error(f"Error adding document type: {str(e)}")
            return False

    async def update_document_type(
        self, document_type_id: str, document_type_data: dict
    ):
        """Update an existing document type"""
        try:
            client = await self.connection.get_client()
            result = await client.update(document_type_id, document_type_data)
            if result:
                self.logger.info(
                    f"Successfully updated document type ID: {document_type_id}"
                )
                return True
            return False
        except Exception as e:
            self.set_error(f"Error updating document type: {str(e)}")
            return False

    async def delete_document_type(self, document_type_id: str):
        """Delete a document type (hard delete)"""
        try:
            client = await self.connection.get_client()
            result = await client.delete(document_type_id)
            if result:
                self.logger.info(
                    f"Successfully deleted document type ID: {document_type_id}"
                )
                return True
            return False
        except Exception as e:
            self.set_error(f"Error deleting document type: {str(e)}")
            return False

    async def get_all_document_types(self, additional_fields: List[str] = None):
        """Get all document types"""
        try:
            client = await self.connection.get_client()
            document_types_list = await client.get_all(additional_fields)
            return document_types_list
        except Exception as e:
            self.set_error(f"Error fetching document types: {str(e)}")
            return []

    async def get_aliases(self, document_type: str):
        """Get aliases for a document type"""
        try:
            client = await self.connection.get_client()
            aliases = await client.get_aliases(document_type)
            return aliases
        except Exception as e:
            self.set_error(f"Error fetching aliases: {str(e)}")
            return []

    async def add_alias(self, document_type: str, alias_name: str):
        """Add an alias for a document type"""
        try:
            client = await self.connection.get_client()
            result = await client.add_alias(document_type, alias_name)
            if result:
                self.logger.info(
                    f"Successfully added alias '{alias_name}' for {document_type}"
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

    def render_add_document_type_form(self):
        """Render the add document type form"""
        st.subheader("Add Document Type")
        document_type = st.text_input("Document Type Name")
        description = st.text_input("Description")
        mime_type = st.text_input("Mime Type")
        file_extension = st.text_input("File Extension")
        category = st.text_input("Category")
        is_ai_generated = st.checkbox("Is AI Generated", value=False)

        if st.button("Add Document Type"):
            document_type_data = {
                "document_type": document_type,
                "description": description,
                "mime_type": mime_type,
                "file_extension": file_extension,
                "category": category,
                "is_ai_generated": is_ai_generated,
            }
            if self.run_async(self.add_document_type(document_type_data)):
                st.success(f"Document Type '{document_type}' added successfully")
                st.rerun()

    def render_edit_document_type_form(self):
        """Render the edit document type form"""
        st.subheader("Edit Document Type")
        document_types_list = self.run_async(
            self.get_all_document_types(
                [
                    "description",
                    "mime_type",
                    "file_extension",
                    "category",
                    "is_ai_generated",
                ]
            )
        )

        if not document_types_list:
            st.warning("No document types found in the database")
            return

        document_type_options = sorted(
            [
                (
                    doc_type["id"],
                    doc_type["document_type"],
                    doc_type.get("description", ""),
                    doc_type.get("mime_type", ""),
                    doc_type.get("file_extension", ""),
                    doc_type.get("category", ""),
                    doc_type.get("is_ai_generated", False),
                )
                for doc_type in document_types_list
            ],
            key=lambda x: x[1],
        )

        selected_document_type = st.selectbox(
            "Select Document Type to Edit",
            document_type_options,
            format_func=lambda x: x[1],
            key="select_document_type_to_edit",
        )

        if selected_document_type:
            selected_document_type_id = selected_document_type[0]
            document_type = st.text_input(
                "Document Type Name", value=selected_document_type[1]
            )
            description = st.text_input("Description", value=selected_document_type[2])
            mime_type = st.text_input("Mime Type", value=selected_document_type[3])
            file_extension = st.text_input(
                "File Extension", value=selected_document_type[4]
            )
            category = st.text_input("Category", value=selected_document_type[5])
            is_ai_generated = st.checkbox(
                "Is AI Generated", value=selected_document_type[6]
            )

            if st.button("Update Document Type"):
                update_document_type = {
                    "document_type": document_type,
                    "description": description,
                    "mime_type": mime_type,
                    "file_extension": file_extension,
                    "category": category,
                    "is_ai_generated": is_ai_generated,
                }
                if self.run_async(
                    self.update_document_type(
                        selected_document_type_id, update_document_type
                    )
                ):
                    st.success(
                        f"Document Type updated successfully for {document_type}"
                    )
                    st.rerun()

    def render_delete_document_type_form(self):
        """Render the delete document type form"""
        st.subheader("Delete Document Type")
        document_types_list = self.run_async(self.get_all_document_types())

        document_type_deletes = sorted(
            [
                (doc_type["id"], doc_type["document_type"])
                for doc_type in document_types_list
            ],
            key=lambda x: x[1],
        )

        selected_document_type = st.selectbox(
            "Select Document Type to Delete",
            document_type_deletes,
            format_func=lambda x: x[1],
            key="select_document_type_to_delete",
        )

        if selected_document_type:
            selected_document_type_id, selected_document_type = selected_document_type
            if st.button("Delete Document Type"):
                self.logger.info(
                    f"Attempting to delete document type: {selected_document_type}"
                )
                if self.run_async(self.delete_document_type(selected_document_type_id)):
                    st.success(
                        f"Document Type '{selected_document_type}' deleted successfully"
                    )
                    st.rerun()

    def render_alias_form(self):
        """Render the alias management form"""
        st.subheader("Alias Document Type")
        document_types_list = self.run_async(self.get_all_document_types())

        document_type_aliases = sorted(
            [
                (doc_type["id"], doc_type["document_type"])
                for doc_type in document_types_list
            ],
            key=lambda x: x[1],
        )

        selected_document_type = st.selectbox(
            "Select Document Type",
            document_type_aliases,
            format_func=lambda x: x[1],
            key="select_document_type_to_alias",
        )

        if selected_document_type:
            selected_document_type_id, selected_document_type = selected_document_type
            alias_name = st.text_input("Alias Name")

            if alias_name and st.button("Add Alias"):
                if self.run_async(self.add_alias(selected_document_type, alias_name)):
                    st.success(f"Alias '{alias_name}' added successfully")
                    st.rerun()

            # Display existing aliases
            aliases = self.run_async(self.get_aliases(selected_document_type))
            if aliases:
                st.subheader(f"Aliases for {selected_document_type}")
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
                st.warning(f"No aliases found for {selected_document_type}")

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
            st.sidebar.title("Manage Document Types")
            st.sidebar.subheader("Actions")
            action = st.sidebar.radio(
                "Select Action", ["Add", "Edit", "Delete", "Alias"]
            )

            if action == "Add":
                self.render_add_document_type_form()
            elif action == "Edit":
                self.render_edit_document_type_form()
            elif action == "Delete":
                self.render_delete_document_type_form()
            elif action == "Alias":
                self.render_alias_form()

        with col2:
            st.subheader("All Document Types")
            document_types_list = self.run_async(
                self.get_all_document_types(
                    [
                        "description",
                        "mime_type",
                        "file_extension",
                        "category",
                        "is_ai_generated",
                    ]
                )
            )
            if document_types_list:
                # Remove 'id' and 'user_id' from each document type dictionary
                for doc_type in document_types_list:
                    doc_type.pop("id", None)
                    doc_type.pop("user_id", None)
                st.dataframe(document_types_list, width=1000, height=600)
            else:
                st.warning("No document types found in the database")


if __name__ == "__main__":
    app = DocumentTypesManager()
    app.main()


# streamlit run st_shared/st_document_types.py
