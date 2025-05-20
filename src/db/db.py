from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.utils.config import player_schema
from src.utils.config import (
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SERVER,
    POSTGRES_USERNAME,
)

DATABASE_URL = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
tables_to_drop = [
    table
    for table in Base.metadata.sorted_tables
    if table.name not in ("systems", "waypoints") or table.schema != player_schema
]

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db():
    # Create schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {player_schema}"))
        conn.commit()
    Base.metadata.drop_all(bind=engine, tables=tables_to_drop)
    # Create tables within the schema
    Base.metadata.create_all(engine)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
