from sqlalchemy import create_engine, text
from src.utils.config import (
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SERVER,
    POSTGRES_USERNAME,
    player_schema,
)


DATABASE_URL = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


# Create engine
engine = create_engine(DATABASE_URL)


def create_schema():
    """Creates the schema in the database if it does not exist."""
    with engine.connect() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {player_schema}"))
        connection.commit()
