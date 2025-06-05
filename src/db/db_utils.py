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
from src.db.models import (
    Ship,
    Agent,
    Module,
    Mount,
    ShipNavigation,
    ShipFuel,
    ShipCargo,
    ShipCrew,
    ShipFrame,
    ShipReactor,
    ShipEngine,
    ShipCooldown,
    ShipTelemetry,
    System,
    Waypoint,
    CargoItem,
)

DATABASE_URL = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def drop_selected_tables(models_to_drop):
    """Drops selected SQLAlchemy models from the database."""
    with engine.begin() as conn:
        for model in models_to_drop:
            table = model.__table__
            if table.schema != player_schema:
                continue
            print(f"Dropping table: {table.fullname}")
            table.drop(bind=engine, checkfirst=True)


# Example usage:
# Only drop ShipCargo and CargoItem tables
if __name__ == "__main__":
    drop_selected_tables([ShipCargo])
