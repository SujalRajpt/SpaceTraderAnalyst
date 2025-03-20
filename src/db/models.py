from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    JSON,
    Float,
    BigInteger,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
SCHEMA_NAME = "test_schema"


class Agent(Base):
    """Stores player (agent) information."""

    __tablename__ = "agents"
    __table_args__ = {"schema": SCHEMA_NAME}  # Specify schema

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_token = Column(
        String, unique=True, nullable=False
    )  # Store unique player token
    current_system = Column(String, default="UNKNOWN", nullable=False)
    current_waypoint = Column(String, default="UNKNOWN", nullable=False)
    credit = Column(BigInteger, default=0, nullable=False)
    starting_faction = Column(String, default="UNKNOWN", nullable=False)

    # Relationship to Ship
    ships = relationship("Ship", back_populates="agent", cascade="all, delete-orphan")


class Ship(Base):
    """Stores ship information for each player."""

    __tablename__ = "ships"
    __table_args__ = {"schema": SCHEMA_NAME}  # Specify schema

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False)  # Ship identifier
    agent_id = Column(Integer, ForeignKey(f"{SCHEMA_NAME}.agents.id"), nullable=False)

    # Navigation
    status = Column(
        Enum("DOCKED", "IN_TRANSIT", "IDLE", name="ship_status"), nullable=False
    )
    system = Column(String, nullable=False)  # Current system
    waypoint = Column(String, nullable=False)  # Current waypoint
    x = Column(Integer, nullable=False)  # X coordinate
    y = Column(Integer, nullable=False)  # Y coordinate

    # Crew
    crew_current = Column(Integer, nullable=False)
    crew_capacity = Column(Integer, nullable=False)
    crew_morale = Column(Integer, nullable=False)

    # Fuel
    fuel_current = Column(Integer, nullable=False)
    fuel_capacity = Column(Integer, nullable=False)

    # Cooldown
    cooldown_seconds = Column(Integer, nullable=False, default=0)

    # Engine
    engine_type = Column(String, nullable=False)
    engine_speed = Column(Float, nullable=False)

    # Cargo
    cargo_capacity = Column(Integer, nullable=False)
    cargo_units = Column(Integer, nullable=False)
    cargo_inventory = Column(JSON, nullable=True)  # Store cargo items in JSON format

    # Relationships
    agent = relationship("Agent", back_populates="ships")

    def __repr__(self):
        return (
            f"<Ship(symbol={self.symbol}, status={self.status}, system={self.system})>"
        )
