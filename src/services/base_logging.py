from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from functools import wraps
import logging
import os
from datetime import datetime
import time
import inspect


class LoggerInterface(ABC):
    @abstractmethod
    def debug(self, message: str) -> None:
        pass

    @abstractmethod
    def info(self, message: str) -> None:
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        pass

    @abstractmethod
    def error(self, message: str, error: Exception = None) -> None:
        pass

    @abstractmethod
    def critical(self, message: str, error: Exception = None) -> None:
        pass

    @abstractmethod
    def exception(self, message: str) -> None:
        """Log exception info with ERROR level (should only be called from an except block)"""
        pass

    @abstractmethod
    def set_level(self, level: int) -> None:
        """Set the logging level"""
        pass

    @abstractmethod
    def get_level(self) -> int:
        """Get the current logging level"""
        pass

    @abstractmethod
    def log_method_call(
        self,
        method_name: str,
        args: tuple,
        kwargs: Dict[str, Any],
        duration: float,
        result: Any = None,
        error: Exception = None,
    ) -> None:
        """Log method entry/exit with parameters and results"""
        pass

    @abstractmethod
    def add_context(self, **kwargs) -> None:
        """Add context information to all subsequent log messages"""
        pass

    @abstractmethod
    def clear_context(self) -> None:
        """Clear any stored context information"""
        pass


class Logger(LoggerInterface):
    def __init__(self, name: str = __name__):
        self._logger = logging.getLogger(name)
        self._log_dir = os.path.join("dhg-source-viewer", "logs")
        os.makedirs(self._log_dir, exist_ok=True)

        # Store current date for comparison
        self._current_date = datetime.now().date()

        # Configure console handler
        console_handler = logging.StreamHandler()
        self._formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(self._formatter)
        self._logger.addHandler(console_handler)

        # Configure initial file handler
        self._update_file_handler()
        self._logger.setLevel(logging.DEBUG)

        self._context = {}
        # Create a formatter without the context first
        self._formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def _update_file_handler(self) -> None:
        # Remove existing file handler if it exists
        for handler in self._logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                self._logger.removeHandler(handler)

        # Create new file handler
        log_file = os.path.join(
            self._log_dir, f"{self._current_date.strftime('%Y-%m-%d')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(self._formatter)
        self._logger.addHandler(file_handler)
        self._logger.info("Log file created")

    def _check_rotate_log(self) -> None:
        current_date = datetime.now().date()
        if current_date != self._current_date:
            self._current_date = current_date
            self._update_file_handler()

    def _format_message(self, message: str) -> str:
        if self._context:
            context_str = " - ".join(f"{k}={v}" for k, v in self._context.items())
            return f"{context_str} - {message}"
        return message

    def debug(self, message: str) -> None:
        self._check_rotate_log()
        self._logger.debug(self._format_message(message))

    def info(self, message: str) -> None:
        self._check_rotate_log()
        self._logger.info(self._format_message(message))

    def warning(self, message: str) -> None:
        self._check_rotate_log()
        self._logger.warning(self._format_message(message))

    def error(self, message: str, error: Exception = None) -> None:
        self._check_rotate_log()
        self._logger.error(self._format_message(message), exc_info=error)

    def critical(self, message: str, error: Exception = None) -> None:
        self._check_rotate_log()
        self._logger.critical(self._format_message(message), exc_info=error)

    def exception(self, message: str) -> None:
        self._check_rotate_log()
        self._logger.exception(self._format_message(message))

    def set_level(self, level: int) -> None:
        self._logger.setLevel(level)

    def get_level(self) -> int:
        return self._logger.getEffectiveLevel()

    def add_context(self, **kwargs) -> None:
        self._context.update(kwargs)

    def clear_context(self) -> None:
        self._context.clear()

    def log_method_call(
        self,
        method_name: str,
        args: tuple,
        kwargs: Dict[str, Any],
        duration: float,
        result: Any = None,
        error: Exception = None,
    ) -> None:
        self._check_rotate_log()
        context = f"method={method_name}"
        if error:
            self._logger.error(
                f"{context} - args={args} kwargs={kwargs} duration={duration:.3f}s - ERROR: {str(error)}",
                exc_info=error,
            )
        else:
            self._logger.debug(
                f"{context} - args={args} kwargs={kwargs} duration={duration:.3f}s - result={result}"
            )


def log_method(logger: Optional[LoggerInterface] = None):
    """Decorator to automatically log method entry/exit with parameters and timing"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            method_name = func.__name__
            current_logger = logger or getattr(args[0], "_logger", None)

            if not current_logger:
                return await func(*args, **kwargs)

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                current_logger.log_method_call(
                    method_name, args, kwargs, duration, result
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                current_logger.log_method_call(
                    method_name, args, kwargs, duration, error=e
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            method_name = func.__name__
            current_logger = logger or getattr(args[0], "_logger", None)

            if not current_logger:
                return func(*args, **kwargs)

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                current_logger.log_method_call(
                    method_name, args, kwargs, duration, result
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                current_logger.log_method_call(
                    method_name, args, kwargs, duration, error=e
                )
                raise

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
