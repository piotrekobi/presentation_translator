import logging
import os
from datetime import datetime
from constants import LOGS_DIR


class Logger:
    def __init__(self, name="speech_translator"):
        os.makedirs(LOGS_DIR, exist_ok=True)
        self.logger = logging.getLogger(name)

        # Clear any existing handlers
        self.logger.handlers = []

        self.logger.setLevel(logging.DEBUG)

        # Add console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Add file handler for persistent logging
        filename = f'speech_translator_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        file_handler = logging.FileHandler(os.path.join(LOGS_DIR, filename))
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        self.logger.propagate = False

        self.logger.info(f"Logger initialized. Logging to {filename}")

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
