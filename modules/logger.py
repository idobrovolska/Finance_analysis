import os
from datetime import datetime


class Logger:
    def __init__(self, log_dir="logs", console_output=True, log_level="INFO"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
        self.console_output = console_output
        self.log_level = log_level
        self.levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}

    def log(self, message, level="INFO"):
        if self.levels.get(level, 1) < self.levels.get(self.log_level, 1):
            return
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        if self.console_output:
            print(log_message)
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")

    def debug(self, message):
        self.log(message, level="DEBUG")

    def info(self, message):
        self.log(message, level="INFO")

    def warning(self, message):
        self.log(message, level="WARNING")

    def error(self, message):
        self.log(message, level="ERROR")
