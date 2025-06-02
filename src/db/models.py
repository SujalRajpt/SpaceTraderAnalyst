from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    BigInteger,
    Index,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from src.utils.config import player_schema
from sqlalchemy import DateTime
from datetime import datetime, timezone
from sqlalchemy.sql import func

# this if for if in future i encouter a probelm where same recored are inserted twice due to some error. this basically will be used to avoid that
from sqlalchemy import UniqueConstraint

Base = declarative_base()


# Player Models
class Agent(Base):
    """Stores player (agent) information."""

    __tablename__ = "agents"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    agent_token = Column(String, unique=True, nullable=False, index=True)
    current_system = Column(String, default="UNKNOWN", nullable=False)
    current_waypoint = Column(String, default="UNKNOWN", nullable=False)
    credit = Column(BigInteger, default=0, nullable=False)
    starting_faction = Column(String, default="UNKNOWN", nullable=False)

    ships = relationship("Ship", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agent(id={self.id}, agent_token={self.agent_token})>"


# ----------------------------
# Ship Table
# ----------------------------
class Ship(Base):
    """Stores only ship symbol and its relationship with an agent."""

    __tablename__ = "ships"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    factionSymbol = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, nullable=False)
    flightMode = Column(String, nullable=False)
    systemSymbol = Column(String, nullable=False)
    # system_id = Column(
    #     Integer, ForeignKey(f"{player_schema}.systems.id"), nullable=False
    # )

    waypointSymbol = Column(String, nullable=False)
    # waypoint_id = Column(
    #     Integer, ForeignKey(f"{player_schema}.waypoints.id"), nullable=False
    # )
    speed = Column(Integer, nullable=False)

    agent_id = Column(Integer, ForeignKey(f"{player_schema}.agents.id"), nullable=False)

    # Relationships
    agent = relationship("Agent", back_populates="ships")
    modules = relationship(
        "Module", back_populates="ship", cascade="all, delete-orphan"
    )
    mounts = relationship("Mount", back_populates="ship", cascade="all, delete-orphan")
    # system = relationship("System", backref="ships")
    # waypoint = relationship("Waypoint", backref="ships")

    def __repr__(self):
        return f"<Ship(symbol={self.symbol})>"


# ----------------------------
# Module Table
# ----------------------------
class Module(Base):
    __tablename__ = "modules"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    symbol = Column(String, nullable=False)
    name = Column(String)
    description = Column(String)
    power = Column(Integer)
    crew = Column(Integer)
    slots = Column(Integer)
    capacity = Column(Integer, nullable=True)

    ship = relationship("Ship", back_populates="modules")

    def __repr__(self):
        return f"<Module(symbol={self.symbol}, ship_id={self.ship_id})>"


# ----------------------------
# Mount Table
# ----------------------------
class Mount(Base):
    __tablename__ = "mounts"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    symbol = Column(String, nullable=False)
    name = Column(String)
    description = Column(String)
    power = Column(Integer)
    crew = Column(Integer)
    strength = Column(Integer)

    ship = relationship("Ship", back_populates="mounts")

    def __repr__(self):
        return f"<Mount(symbol={self.symbol}, ship_id={self.ship_id})>"


class ShipNavigation(Base):
    __tablename__ = "ship_navigation"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    origin_waypoint = Column(String, nullable=False)
    origin_system = Column(String, nullable=False)
    destination_waypoint = Column(String, nullable=False)
    destination_system = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    flightMode = Column(String, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    ship = relationship("Ship", backref="ship_navigation")

    def __repr__(self):
        return f"<Mount(symbol={self.symbol}, ship_id={self.ship_id})>"


# ----------------------------
# Subcomponent Tables
# ----------------------------


class ShipFuel(Base):
    __tablename__ = "ship_fuel"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    ship = relationship("Ship", backref="ship_fuel")
    current = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    consumed = Column(Integer, nullable=False)
    last_updated = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class ShipCargo(Base):
    __tablename__ = "ship_cargo"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    ship = relationship("Ship", backref="ship_cargo")
    current = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    inventory = Column(ARRAY(String), nullable=True)
    last_updated = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class ShipCrew(Base):
    __tablename__ = "ship_crew"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    ship = relationship("Ship", backref="ship_crew")
    current = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    required = Column(Integer, nullable=False)
    rotation = Column(String, nullable=False)
    morale = Column(Integer, nullable=False)
    wages = Column(Integer, nullable=False)
    last_updated = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class ShipFrame(Base):
    __tablename__ = "ship_frame"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    ship = relationship("Ship", backref="ship_frame")
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    condition = Column(Integer, nullable=False)
    integrity = Column(Integer, nullable=False)
    module_slots = Column(Integer, nullable=False)
    mounting_points = Column(Integer, nullable=False)
    power_required = Column(Integer, nullable=False)
    crew_required = Column(Integer, nullable=False)
    last_updated = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class ShipReactor(Base):
    __tablename__ = "ship_reactor"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    ship = relationship("Ship", backref="ship_reactor")
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    condition = Column(Integer, nullable=False)
    integrity = Column(Integer, nullable=False)
    power_output = Column(Integer, nullable=False)
    crew_required = Column(Integer, nullable=False)
    quality = Column(Integer, nullable=False)
    last_updated = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class ShipEngine(Base):
    __tablename__ = "ship_engine"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    ship = relationship("Ship", backref="ship_engine")
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    condition = Column(Integer, nullable=False)
    integrity = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    power_required = Column(Integer, nullable=False)
    crew_required = Column(Integer, nullable=False)
    quality = Column(Integer, nullable=False)
    last_updated = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class ShipCooldown(Base):
    __tablename__ = "ship_cooldown"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    ship = relationship("Ship", backref="ship_cooldown")
    total_seconds = Column(Integer, nullable=False)
    remaining_seconds = Column(Integer, nullable=False)
    last_updated = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


# ----------------------------
# Main ShipTelemetry Table
# ----------------------------


class ShipTelemetry(Base):
    __tablename__ = "ship_telemetry"
    __table_args__ = {"schema": player_schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ship_id = Column(
        Integer, ForeignKey(f"{player_schema}.ships.id"), nullable=False, index=True
    )
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Foreign keys to subcomponents
    fuel_id = Column(Integer, ForeignKey(f"{player_schema}.ship_fuel.id"))
    cargo_id = Column(Integer, ForeignKey(f"{player_schema}.ship_cargo.id"))
    crew_id = Column(Integer, ForeignKey(f"{player_schema}.ship_crew.id"))
    frame_id = Column(Integer, ForeignKey(f"{player_schema}.ship_frame.id"))
    reactor_id = Column(Integer, ForeignKey(f"{player_schema}.ship_reactor.id"))
    engine_id = Column(Integer, ForeignKey(f"{player_schema}.ship_engine.id"))
    cooldown_id = Column(Integer, ForeignKey(f"{player_schema}.ship_cooldown.id"))

    # Relationships
    fuel = relationship("ShipFuel")
    cargo = relationship("ShipCargo")
    crew = relationship("ShipCrew")
    frame = relationship("ShipFrame")
    reactor = relationship("ShipReactor")
    engine = relationship("ShipEngine")
    cooldown = relationship("ShipCooldown")

    ship = relationship("Ship", backref="ship_telemetry")

    def __repr__(self):
        return f"<ShipTelemetry(id={self.id}, ship_id={self.ship_id}, timestamp={self.timestamp})>"


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
