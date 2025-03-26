import logging
import os

# Ensure the logs/ directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(LOG_DIR, "app.log")
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log to file
        logging.StreamHandler(),  # Log to console
    ],
)

# Create a logger instance
logger = logging.getLogger("spacetraders")
# 🔴 **Suppress SQLAlchemy Logs (Add this part below)**
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # Hide query logs

# Or, completely disable all SQLAlchemy logs:
# logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

# 🔴 **Alternative: Disable SQL logs completely (Optional)**
# logging.getLogger("sqlalchemy.engine").disabled = True

logger.info("Application started.")
