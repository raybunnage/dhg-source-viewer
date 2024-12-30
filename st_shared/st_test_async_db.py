# ... existproject_root = str(Path(__file__).parent.parent)
import streamlit as st
from pathlib import Path
import sys

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from st_shared.streamlit_base import StreamlitBase

from src.services.supabase_service import SupabaseService
from src.db.experts import Experts



class AsyncSupabaseConnection:
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


class TestAsyncDB(StreamlitBase):
    def __init__(self):
        super().__init__("test_async_db")
        self.connection = self._get_connection()

    @staticmethod
    @st.cache_resource
    def _get_connection():
        """Cache the connection instance"""
        return AsyncSupabaseConnection()

    async def load_expert_data(self, expert_id: str):
        """Async function to load expert data"""
        try:
            client = await self.connection.get_client()
            data = await client.get_by_id(expert_id)
            st.session_state.app_state.data = data
            self.clear_error()
            return data
        except Exception as e:
            self.set_error(f"Error loading expert data: {e}")
            raise

    def main(self):
        st.title("Test Async DB")

        # Initialize connection
        if not st.session_state.app_state.is_initialized:
            try:
                self.run_async(self.connection.initialize())
            except Exception as e:
                self.set_error(str(e))

        # Show any errors
        self.show_error()

        # UI Elements
        if st.button("Run CRUD Test"):
            try:
                self.run_async(
                    self.load_expert_data("34acaa61-7fb4-4c02-b463-a55128e354f3")
                )
            except Exception:
                pass  # Error is already handled

        # Show loaded expert data
        if st.session_state.app_state.data:
            st.subheader("Expert Details")
            st.json(st.session_state.app_state.data)
            self.logger.info(f"Expert data: {st.session_state.app_state.data}")

        # Add this test button
        if st.button("Test Logging"):
            self.logger.debug("This is a debug message")
            self.logger.info("This is an info message")
            self.logger.warning("This is a warning message")
            self.logger.error("This is an error message")
            st.success("Logs written! Check the logs directory.")


if __name__ == "__main__":
    app = TestAsyncDB()
    app.main()

# streamlit run st_shared/st_test_async_db.py
