"""Main entry point for MyFinGPT"""

# Load environment variables first, before importing any other modules
from dotenv import load_dotenv
load_dotenv()

# Configure logging before importing other modules
from src.utils.logging_config import setup_logging
import os

# Setup logging
log_dir = os.getenv("LOG_DIR", "./logs")
log_level = os.getenv("LOG_LEVEL", "INFO")
logging_config = setup_logging(log_dir=log_dir, log_level=log_level)

from src.ui.gradio_app import main

if __name__ == "__main__":
    main()

