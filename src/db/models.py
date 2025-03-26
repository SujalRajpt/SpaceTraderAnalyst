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
    """Stores only ship symbol and its relationship with an agent."""

    __tablename__ = "ships"
    __table_args__ = {"schema": SCHEMA_NAME}  # Specify schema

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False)  # Ship identifier
    agent_id = Column(Integer, ForeignKey(f"{SCHEMA_NAME}.agents.id"), nullable=False)

    # Relationship with Agent
    agent = relationship("Agent", back_populates="ships")

    def __repr__(self):
        return f"<Ship(symbol={self.symbol})>"
