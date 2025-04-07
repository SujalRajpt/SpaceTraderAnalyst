import logging
import os
import sys

# Ensure the logs/ directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Paths
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Formatter
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# File handler (logs everything)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Console handler (INFO and above only)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configure root logger
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

# Create named logger
logger = logging.getLogger("spacetraders")

# Suppress noisy logs (optional tweaks)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# To completely silence SQL logs:
# logging.getLogger("sqlalchemy").disabled = True

logger.info("Application started.")
