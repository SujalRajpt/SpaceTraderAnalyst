# config.example.py
# Copy this file to `config.py` and fill in the actual values.

ACC_TOKEN = "your_token_here"
BASE_URL = "https://api.spacetraders.io/v2"

POSTGRES_USERNAME = "your_username_here"
POSTGRES_PASSWORD = "your_password_here"
POSTGRES_SERVER = "your_server_here"
POSTGRES_PORT = "5432"
POSTGRES_DB = "your_database_here"

DATABASE_URL = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
