from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    BigInteger,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from src.utils.config import player_schema
from sqlalchemy import DateTime
from datetime import datetime, timezone

Base = declarative_base()


# Player Models
class Agent(Base):
    """Stores player (agent) information."""

    __tablename__ = "agents"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_token = Column(String, unique=True, nullable=False, index=True)
    current_system = Column(String, default="UNKNOWN", nullable=False)
    current_waypoint = Column(String, default="UNKNOWN", nullable=False)
    credit = Column(BigInteger, default=0, nullable=False)
    starting_faction = Column(String, default="UNKNOWN", nullable=False)

    ships = relationship("Ship", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agent(id={self.id}, agent_token={self.agent_token})>"


class Ship(Base):
    """Stores only ship symbol and its relationship with an agent."""

    __tablename__ = "ships"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey(f"{player_schema}.agents.id"), nullable=False)

    agent = relationship("Agent", back_populates="ships")

    def __repr__(self):
        return f"<Ship(symbol={self.symbol})>"


class System(Base):
    """Stores system information."""

    __tablename__ = "systems"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    constellation = Column(String, nullable=False)
    name = Column(String, nullable=False)
    sector_symbol = Column(String, nullable=False)
    location = Column(Geometry("POINT", srid=0), nullable=False)

    waypoints = relationship(
        "Waypoint", back_populates="system", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<System(id={self.id}, symbol={self.symbol})>"


class Waypoint(Base):
    """Stores waypoint information."""

    __tablename__ = "waypoints"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    waypoint_symbol = Column(String, unique=True, nullable=False)
    waypoint_type = Column(String, nullable=False)
    waypoint_location = Column(Geometry("POINT", srid=0), nullable=False, index=True)

    system_id = Column(
        Integer, ForeignKey(f"{player_schema}.systems.id"), nullable=False, index=True
    )
    parent_waypoint_id = Column(
        Integer, ForeignKey(f"{player_schema}.waypoints.id"), nullable=True
    )

    system = relationship("System", back_populates="waypoints", lazy="joined")
    parent_waypoint = relationship(
        "Waypoint",
        remote_side=[id],
        backref="orbitals",
        cascade="all",
        single_parent=True,  # Enforce single parent
    )

    def __repr__(self):
        return f"<Waypoint(id={self.id}, waypoint_symbol={self.waypoint_symbol})>"


# Create GIST Index for Spatial Data
Index("ix_waypoints_location", Waypoint.waypoint_location, postgresql_using="gist")


class MarketTradeGoods(Base):
    """Stores market trade goods information."""

    __tablename__ = "market_trade_goods"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    waypoint_id = Column(
        Integer, ForeignKey(f"{player_schema}.waypoints.id"), nullable=False
    )

    product_symbol = Column(String, nullable=False)
    trade_volume = Column(Integer, nullable=False)
    type = Column(String, nullable=False, index=True)
    supply = Column(String, nullable=False)
    activity = Column(String, nullable=False)
    purchase_price = Column(Integer, nullable=False)
    sell_price = Column(Integer, nullable=False)
    demand = Column(String, nullable=False, index=True)
    last_updated = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    waypoint = relationship("Waypoint", backref="market_trade_goods")

    def __repr__(self):
        return f"<MarketTradeGoods(id={self.id}, good_id={self.product_symbol})>"


Index("ix_waypoint_product", "waypoint_id", "product_symbol")
