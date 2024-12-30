import streamlit as st
import logging
from pathlib import Path
import sys
from typing import Optional
import asyncio
from dataclasses import dataclass

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
from src.services.supabase_service import SupabaseService
from src.db.experts import Experts
from src.db.base_db import BaseDB


class StreamlitLogger(BaseDB):
    def __init__(self):
        super().__init__(log_level=logging.DE)


logger_instance = StreamlitLogger()
logger = logger_instance.logger


@dataclass
class AppState:
    """Class to manage application state"""

    is_initialized: bool = False
    last_error: Optional[str] = None
    expert_data: Optional[dict] = None


def init_session_state():
    """Initialize session state with default values"""
    if "app_state" not in st.session_state:
        st.session_state.app_state = AppState()


class AsyncSupabaseConnection:
    def __init__(self):
        self.client: Optional[Experts] = None
        self._initialized = False
        init_session_state()

    async def initialize(self):
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
                st.session_state.app_state.last_error = None
            except Exception as e:
                error_msg = f"Failed to initialize Supabase connection: {e}"
                logger.error(error_msg)
                st.session_state.app_state.last_error = error_msg
                raise

    async def get_client(self) -> Experts:
        if not self._initialized:
            await self.initialize()
        return self.client


@st.cache_resource
def get_connection():
    """Cache the connection instance"""
    return AsyncSupabaseConnection()


@st.cache_resource
def get_event_loop():
    """Get or create an event loop - cached to prevent multiple loops"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def run_async(coro):
    """Execute async code in Streamlit"""
    loop = get_event_loop()
    return loop.run_until_complete(coro)


async def load_expert_data(expert_id: str):
    """Async function to load expert data"""
    try:
        conn = get_connection()
        client = await conn.get_client()
        data = await client.get_by_id(expert_id)
        st.session_state.app_state.expert_data = data
        st.session_state.app_state.last_error = None
        return data
    except Exception as e:
        error_msg = f"Error loading expert data: {e}"
        st.session_state.app_state.last_error = error_msg
        raise


def main():
    st.title("Test Async DB")

    # Initialize session state first
    init_session_state()

    # Initialize connection
    if not st.session_state.app_state.is_initialized:
        try:
            run_async(get_connection().initialize())
        except Exception:
            pass  # Error is stored in session state

    # Show any errors
    if st.session_state.app_state.last_error:
        st.error(st.session_state.app_state.last_error)

    # UI Elements
    if st.button("Run CRUD Test"):
        try:
            expert_data = run_async(
                load_expert_data("34acaa61-7fb4-4c02-b463-a55128e354f3")
            )
        except Exception:
            pass  # Error is already stored in session state

    # Show loaded expert data
    if st.session_state.app_state.expert_data:
        st.subheader("Expert Details")
        st.json(st.session_state.app_state.expert_data)
        logger.info(f"Expert data: {st.session_state.app_state.expert_data}")

    # Add this test button
    if st.button("Test Logging"):
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        st.success("Logs written! Check the logs directory.")


if __name__ == "__main__":
    main()

# streamlit run st_shared/st_test_aysync_db.py
