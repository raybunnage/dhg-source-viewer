import logging
from datetime import datetime
from pathlib import Path


class BaseDB:
    def __init__(self, log_level=logging.INFO):
        self.setup_logging(log_level)

    def setup_logging(self, log_level):
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create a logger for this instance
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

        # Only add handlers if they haven't been added yet
        if not self.logger.handlers:
            # File handler - separate file for each day
            file_handler = logging.FileHandler(
                log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter("%(name)s - %(levelname)s - %(message)s")
            )

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def clear_logs(self):
        log_dir = Path("logs")
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        print(f"log_file: {log_file} log_dir: {log_dir}")
        with open(log_file, "w") as f:
            f.truncate(0)


if __name__ == "__main__":
    db = BaseDB()
    db.clear_logs()
