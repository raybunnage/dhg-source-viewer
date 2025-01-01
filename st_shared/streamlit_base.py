import streamlit as st
import logging
from pathlib import Path
import sys
import asyncio
from dataclasses import dataclass
from typing import Optional

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)


@dataclass
class AppState:
    """Class to manage application state"""

    is_initialized: bool = False
    last_error: Optional[str] = None
    data: Optional[dict] = None


class StreamlitBase:
    def __init__(self, module_name: str):
        self.logger = self._setup_logger(module_name)
        self._init_session_state()

    def _setup_logger(self, module_name: str):
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.DEBUG)
        # Create console handler with formatting
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def _init_session_state(self):
        """Initialize session state with default values"""
        if "app_state" not in st.session_state:
            st.session_state.app_state = AppState()

    @staticmethod
    @st.cache_resource
    def _get_event_loop():
        """Get or create an event loop - cached to prevent multiple loops"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    def run_async(self, coro):
        """Execute async code in Streamlit"""
        loop = self._get_event_loop()
        return loop.run_until_complete(coro)

    def show_error(self):
        """Display error message if present"""
        if st.session_state.app_state.last_error:
            st.error(st.session_state.app_state.last_error)

    def set_error(self, error_msg: str):
        """Set error message in session state"""
        st.session_state.app_state.last_error = error_msg
        self.logger.error(error_msg)

    def clear_error(self):
        """Clear error message from session state"""
        st.session_state.app_state.last_error = None

    def _validate_data(self, data):
        # Add implementation here - for example:
        pass  # or your actual validation logic
