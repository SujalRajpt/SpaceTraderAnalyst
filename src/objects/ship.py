from geoalchemy2.functions import ST_Distance
from src.utils.config import BASE_URL
from src.api.base_api import BaseAPI
from src.utils.logger import logger
from src.db.db_session import get_session
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
from datetime import datetime


class ShipDB:
    def __init__(self, ship):
        self.ship = ship
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.ship.shipSymbol}"

    def get_distance_to_waypoint(self, my_waypoint=None, destination_waypoint=None):
        """Calculates the distance to a given waypoint."""
        with get_session() as session:
            wp_a = (
                session.query(Waypoint)
                .filter(
                    Waypoint.waypoint_symbol
                    == (my_waypoint or self.ship.waypointSymbol)
                )
                .first()
            )
            wp_b = (
                session.query(Waypoint)
                .filter(Waypoint.waypoint_symbol == destination_waypoint)
                .first()
            )

            if not wp_a or not wp_b:
                raise ValueError("One or both waypoints not found.")

            return session.query(
                ST_Distance(wp_a.waypoint_location, wp_b.waypoint_location)
            ).scalar()

    # Get ship data from the database
    def fetch_modules_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return []

            modules = session.query(Module).filter_by(ship_id=ship.id).all()
            if not modules:
                logger.warning(
                    f"No modules found for ship {self.ship.shipSymbol} in DB."
                )
                return []

            logger.info(
                f"Fetched {len(modules)} modules for ship {self.ship.shipSymbol} from DB."
            )

            # Convert ORM instances to plain dicts BEFORE returning
            return [
                {
                    "id": module.id,
                    "ship_id": ship.id,
                    "name": module.name,
                    "symbol": module.symbol,
                    "power": module.power,
                    "crew": module.crew,
                    "slots": module.slots,
                    "capacity": module.capacity,
                }
                for module in modules
            ]

    def fetch_mounts_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return []

            mounts = session.query(Mount).filter_by(ship_id=ship.id).all()
            if not mounts:
                logger.warning(
                    f"No mounts found for ship {self.ship.shipSymbol} in DB."
                )
                return []

            logger.info(
                f"Fetched {len(mounts)} mounts for ship {self.ship.shipSymbol} from DB."
            )

            # Convert ORM instances to plain dicts BEFORE returning
            return [
                {
                    "id": mount.id,
                    "ship_id": ship.id,
                    "name": mount.name,
                    "symbol": mount.symbol,
                    "power": mount.power,
                    "crew": mount.crew,
                    "strength": mount.strength,
                }
                for mount in mounts
            ]

    def fetch_navigation_info_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return None

            ship_nav = session.query(ShipNavigation).filter_by(ship_id=ship.id).first()
            if not ship_nav:
                logger.warning(
                    f"No navigation info found for ship {self.ship.shipSymbol} in DB."
                )
                return None

            logger.info(
                f"Fetched navigation info for ship {self.ship.shipSymbol} from DB."
            )
            return {
                "origin_waypoint": ship_nav.origin_waypoint,
                "origin_system": ship_nav.origin_system,
                "destination_waypoint": ship_nav.destination_waypoint,
                "destination_system": ship_nav.destination_system,
                "departure_time": ship_nav.departure_time.isoformat()
                if ship_nav.departure_time
                else None,
                "arrival_time": ship_nav.arrival_time.isoformat()
                if ship_nav.arrival_time
                else None,
                "status": ship_nav.status,
                "flight_mode": ship_nav.flightMode,
            }

    def fetch_shipfuel_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return None

            ship_fuel = session.query(ShipFuel).filter_by(ship_id=ship.id).first()
            if not ship_fuel:
                logger.warning(
                    f"No fuel info found for ship {self.ship.shipSymbol} in DB."
                )
                return None

            logger.info(f"Fetched fuel info for ship {self.ship.shipSymbol} from DB.")
            return {
                "ship_id": ship.id,
                "current": ship_fuel.current,
                "capacity": ship_fuel.capacity,
                "consumed": ship_fuel.consumed,
                "last_updated": ship_fuel.last_updated.isoformat()
                if ship_fuel.last_updated
                else None,
            }

    def fetch_shipcargo_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return None

            ship_cargo = session.query(ShipCargo).filter_by(ship_id=ship.id).first()
            if not ship_cargo:
                logger.warning(
                    f"No cargo info found for ship {self.ship.shipSymbol} in DB."
                )
                return None

            # Fetch all cargo items for this ship_cargo
            cargo_items = (
                session.query(CargoItem).filter_by(ship_cargo_id=ship_cargo.id).all()
            )

            inventory = [
                {
                    "id": item.id,
                    "symbol": item.symbol,
                    "units": item.units,
                    "last_updated": item.last_updated.isoformat()
                    if item.last_updated
                    else None,
                }
                for item in cargo_items
            ]

            logger.info(f"Fetched cargo info for ship {self.ship.shipSymbol} from DB.")
            return {
                "ship_id": ship.id,
                "current_capacity": ship_cargo.current,
                "Total_capacity": ship_cargo.capacity,
                "last_updated": ship_cargo.last_updated.isoformat()
                if ship_cargo.last_updated
                else None,
                "inventory": inventory,
            }

    def fetch_shipcrew_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return None

            ship_crew = session.query(ShipCrew).filter_by(ship_id=ship.id).first()
            if not ship_crew:
                logger.warning(
                    f"No crew info found for ship {self.ship.shipSymbol} in DB."
                )
                return None

            logger.info(f"Fetched crew info for ship {self.ship.shipSymbol} from DB.")
            return {
                "ship_id": ship.id,
                "current": ship_crew.current,
                "capacity": ship_crew.capacity,
                "required": ship_crew.required,
                "rotation": ship_crew.rotation,
                "morale": ship_crew.morale,
                "wages": ship_crew.wages,
                "last_updated": ship_crew.last_updated.isoformat()
                if ship_crew.last_updated
                else None,
            }

    def fetch_shipframe_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return None

            ship_frame = session.query(ShipFrame).filter_by(ship_id=ship.id).first()
            if not ship_frame:
                logger.warning(
                    f"No frame info found for ship {self.ship.shipSymbol} in DB."
                )
                return None

            logger.info(f"Fetched frame info for ship {self.ship.shipSymbol} from DB.")
            return {
                "ship_id": ship.id,
                "symbol": ship_frame.symbol,
                "name": ship_frame.name,
                "condition": ship_frame.condition,
                "integrity": ship_frame.integrity,
                "module_slots": ship_frame.module_slots,
                "mounting_points": ship_frame.mounting_points,
                "power_required": ship_frame.power_required,
                "crew_required": ship_frame.crew_required,
                "last_updated": ship_frame.last_updated.isoformat()
                if ship_frame.last_updated
                else None,
            }

    def fetch_shipreactor_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return None

            ship_reactor = session.query(ShipReactor).filter_by(ship_id=ship.id).first()
            if not ship_reactor:
                logger.warning(
                    f"No reactor info found for ship {self.ship.shipSymbol} in DB."
                )
                return None

            logger.info(
                f"Fetched reactor info for ship {self.ship.shipSymbol} from DB."
            )
            return {
                "ship_id": ship.id,
                "symbol": ship_reactor.symbol,
                "name": ship_reactor.name,
                "condition": ship_reactor.condition,
                "integrity": ship_reactor.integrity,
                "power_output": ship_reactor.power_output,
                "crew_required": ship_reactor.crew_required,
                "quality": ship_reactor.quality,
                "last_updated": ship_reactor.last_updated.isoformat()
                if ship_reactor.last_updated
                else None,
            }

    def fetch_shipengine_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return None

            ship_engine = session.query(ShipEngine).filter_by(ship_id=ship.id).first()
            if not ship_engine:
                logger.warning(
                    f"No engine info found for ship {self.ship.shipSymbol} in DB."
                )
                return None

            logger.info(f"Fetched engine info for ship {self.ship.shipSymbol} from DB.")
            return {
                "ship_id": ship.id,
                "symbol": ship_engine.symbol,
                "name": ship_engine.name,
                "condition": ship_engine.condition,
                "integrity": ship_engine.integrity,
                "speed": ship_engine.speed,
                "power_required": ship_engine.power_required,
                "crew_required": ship_engine.crew_required,
                "quality": ship_engine.quality,
                "last_updated": ship_engine.last_updated.isoformat()
                if ship_engine.last_updated
                else None,
            }

    def fetch_shipcooldown_from_db(self):
        with get_session() as session:
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return None

            ship_cooldown = (
                session.query(ShipCooldown).filter_by(ship_id=ship.id).first()
            )
            if not ship_cooldown:
                logger.warning(
                    f"No cooldown info found for ship {self.ship.shipSymbol} in DB."
                )
                return None

            logger.info(
                f"Fetched cooldown info for ship {self.ship.shipSymbol} from DB."
            )
            return {
                "ship_id": ship.id,
                "total_seconds": ship_cooldown.total_seconds,
                "remaining_seconds": ship_cooldown.remaining_seconds,
                "last_updated": ship_cooldown.last_updated.isoformat()
                if ship_cooldown.last_updated
                else None,
            }


class Telemetry:
    def __init__(self, ship):
        self.ship = ship
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.ship.shipSymbol}"

    def update_modules(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return "not_found"
            modules_data = ship_info.get("data", {}).get("modules", [])

            if not modules_data:
                logger.warning(
                    f"No modules found in ship_info for ship {self.ship.shipSymbol}"
                )
                return "no_modules"

            for mod_data in modules_data:
                symbol = mod_data.get("symbol")
                if not symbol:
                    continue  # Skip invalid entries

                existing_module = (
                    session.query(Module)
                    .filter(Module.ship_id == ship.id, Module.symbol == symbol)
                    .first()
                )

                requirements = mod_data.get("requirements", {})

                if existing_module:
                    existing_module.power = requirements.get("power")
                    existing_module.crew = requirements.get("crew")
                    existing_module.slots = requirements.get("slots")
                    existing_module.capacity = requirements.get("capacity")
                else:
                    new_module = Module(
                        ship_id=ship.id,
                        name=mod_data.get("name"),
                        description=mod_data.get("description"),
                        symbol=symbol,
                        power=requirements.get("power"),
                        crew=requirements.get("crew"),
                        slots=requirements.get("slots"),
                        capacity=requirements.get("capacity"),
                    )
                    session.add(new_module)
            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_mounts(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return
            for mount_data in ship_info["data"]["mounts"]:
                existing_mount = (
                    session.query(Mount)
                    .filter(
                        Mount.ship_id == ship.id,
                        Mount.symbol == mount_data.get("symbol"),
                    )
                    .first()
                )

                requirements = mount_data.get("requirements", {})

                if existing_mount:
                    existing_mount.power = requirements.get("power")
                    existing_mount.crew = requirements.get("crew")
                else:
                    new_mount = Mount(
                        ship_id=ship.id,
                        name=mount_data.get("name"),
                        description=mount_data.get("description"),
                        symbol=mount_data.get("symbol"),
                        power=requirements.get("power"),
                        crew=requirements.get("crew"),
                        strength=mount_data.get("strength"),
                    )
                    session.add(new_mount)

            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_ShipNavigation(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return
            ship_nav = session.query(ShipNavigation).filter_by(ship_id=ship.id).first()
            nav_data = ship_info.get("data", {}).get("nav", {})
            route_data = nav_data.get("route", {})
            origin_system = route_data.get("origin")
            destination_system = route_data.get("destination")
            if ship_nav:
                ship_nav.origin_waypoint = origin_system.get("symbol")
                ship_nav.origin_system = origin_system.get("systemSymbol")
                ship_nav.destination_waypoint = destination_system.get("symbol")
                ship_nav.destination_system = destination_system.get("systemSymbol")
                ship_nav.departure_time = route_data.get("departureTime")
                ship_nav.arrival_time = route_data.get("arrival")
                ship_nav.status = nav_data.get("status")
                ship_nav.flight_mode = nav_data.get("flightMode")

            else:
                ship_nav = ShipNavigation(
                    ship_id=ship.id,
                    origin_waypoint=origin_system.get("symbol"),
                    origin_system=origin_system.get("systemSymbol"),
                    destination_waypoint=destination_system.get("symbol"),
                    destination_system=destination_system.get("systemSymbol"),
                    departure_time=route_data.get("departureTime"),
                    arrival_time=route_data.get("arrival"),
                    status=nav_data.get("status"),
                    flightMode=nav_data.get("flightMode"),
                )
                session.add(ship_nav)
            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_ShipFuel(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return

            fuel_data = ship_info.get("data", {}).get("fuel", {})
            consumed_data = fuel_data.get("consumed", {})

            if not fuel_data:
                logger.warning(f"No fuel data found for ship {self.ship.shipSymbol}.")
                return

            ship_fuel = session.query(ShipFuel).filter_by(ship_id=ship.id).first()

            if ship_fuel:
                ship_fuel.current = fuel_data.get("current", 0)
                ship_fuel.capacity = fuel_data.get("capacity", 0)
                ship_fuel.consumed = consumed_data.get("amount", 0)
            else:
                ship_fuel = ShipFuel(
                    ship_id=ship.id,
                    current=fuel_data.get("current", 0),
                    capacity=fuel_data.get("capacity", 0),
                    consumed=consumed_data.get("amount", 0),
                )
                session.add(ship_fuel)

            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_cargo_item(self, session=None, cargo_info=None, cargo_id=None):
        """Updates the cargo items in the database.
        It should never be called directly, only through update_ShipCargo.
        So it will always have session and ship_info available."""
        for inventory_data in cargo_info:
            cargo_db = (
                session.query(CargoItem)
                .filter_by(
                    ship_cargo_id=cargo_id, symbol=inventory_data.get("symbol", "")
                )
                .first()
            )
            if cargo_db:
                cargo_db.units = inventory_data.get("units", 0)
            else:
                cargo_db = CargoItem(
                    ship_cargo_id=cargo_id,
                    symbol=inventory_data.get("symbol", ""),
                    units=inventory_data.get("units", 0),
                )
                session.add(cargo_db)

    def update_ShipCargo(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return

            cargo_data = ship_info.get("data", {}).get("cargo", {})
            if not cargo_data:
                logger.warning(f"No cargo data found for ship {self.ship.shipSymbol}.")
                return

            ship_cargo = session.query(ShipCargo).filter_by(ship_id=ship.id).first()

            if ship_cargo:
                ship_cargo.current = cargo_data.get("units", 0)
                ship_cargo.capacity = cargo_data.get("capacity", 0)
            else:
                ship_cargo = ShipCargo(
                    ship_id=ship.id,
                    current=cargo_data.get("units", 0),
                    capacity=cargo_data.get("capacity", 0),
                )
                session.add(ship_cargo)
                session.flush()

            cargo_id = ship_cargo.id

            inventory_items = cargo_data.get("inventory", [])

            if inventory_items:
                self.update_cargo_item(
                    session=session, cargo_info=inventory_items, cargo_id=cargo_id
                )

            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_ShipCrew(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return

            crew_data = ship_info.get("data", {}).get("crew", {})
            if not crew_data:
                logger.warning(f"No crew data found for ship {self.ship.shipSymbol}.")
                return

            ship_crew = session.query(ShipCrew).filter_by(ship_id=ship.id).first()

            if ship_crew:
                ship_crew.current = crew_data.get("current", 0)
                ship_crew.capacity = crew_data.get("capacity", 0)
                ship_crew.required = crew_data.get("required", 0)
                ship_crew.rotation = crew_data.get("rotation", 0)
                ship_crew.morale = crew_data.get("morale", 0)
                ship_crew.wages = crew_data.get("wages", 0)
            else:
                ship_crew = ShipCrew(
                    ship_id=ship.id,
                    current=crew_data.get("current", 0),
                    capacity=crew_data.get("capacity", 0),
                    required=crew_data.get("required", 0),
                    rotation=crew_data.get("rotation", 0),
                    morale=crew_data.get("morale", 0),
                    wages=crew_data.get("wages", 0),
                )
                session.add(ship_crew)

            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_ShipFrame(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return

            frame_data = ship_info.get("data", {}).get("frame", {})
            if not frame_data:
                logger.warning(f"No frame data found for ship {self.ship.shipSymbol}.")
                return

            requirements = frame_data.get("requirements", {})
            ship_frame = session.query(ShipFrame).filter_by(ship_id=ship.id).first()

            if ship_frame:
                ship_frame.symbol = frame_data.get("symbol", "")
                ship_frame.name = frame_data.get("name", "")
                ship_frame.condition = frame_data.get("condition", 0)
                ship_frame.integrity = frame_data.get("integrity", 0)
                ship_frame.module_slots = frame_data.get("moduleSlots", 0)
                ship_frame.mounting_points = frame_data.get("mountingPoints", 0)
                ship_frame.power_required = requirements.get("power", 0)
                ship_frame.crew_required = requirements.get("crew", 0)
            else:
                ship_frame = ShipFrame(
                    ship_id=ship.id,
                    symbol=frame_data.get("symbol", ""),
                    name=frame_data.get("name", ""),
                    condition=frame_data.get("condition", 0),
                    integrity=frame_data.get("integrity", 0),
                    module_slots=frame_data.get("moduleSlots", 0),
                    mounting_points=frame_data.get("mountingPoints", 0),
                    power_required=requirements.get("power", 0),
                    crew_required=requirements.get("crew", 0),
                )
                session.add(ship_frame)

            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_ShipReactor(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return

            reactor_data = ship_info.get("data", {}).get("reactor", {})
            if not reactor_data:
                logger.warning(
                    f"No reactor data found for ship {self.ship.shipSymbol}."
                )
                return

            requirements = reactor_data.get("requirements", {})
            ship_reactor = session.query(ShipReactor).filter_by(ship_id=ship.id).first()

            if ship_reactor:
                ship_reactor.symbol = reactor_data.get("symbol", "")
                ship_reactor.name = reactor_data.get("name", "")
                ship_reactor.condition = reactor_data.get("condition", 0)
                ship_reactor.integrity = reactor_data.get("integrity", 0)
                ship_reactor.power_output = reactor_data.get("powerOutput", 0)
                ship_reactor.crew_required = requirements.get("crew", 0)
                ship_reactor.quality = reactor_data.get("quality", 0)
            else:
                ship_reactor = ShipReactor(
                    ship_id=ship.id,
                    symbol=reactor_data.get("symbol", ""),
                    name=reactor_data.get("name", ""),
                    condition=reactor_data.get("condition", 0),
                    integrity=reactor_data.get("integrity", 0),
                    power_output=reactor_data.get("powerOutput", 0),
                    crew_required=requirements.get("crew", 0),
                    quality=reactor_data.get("quality", 0),
                )
                session.add(ship_reactor)

            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_ShipEngine(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return

            engine_data = ship_info.get("data", {}).get("engine", {})
            if not engine_data:
                logger.warning(f"No engine data found for ship {self.ship.shipSymbol}.")
                return

            requirements = engine_data.get("requirements", {})
            ship_engine = session.query(ShipEngine).filter_by(ship_id=ship.id).first()

            if ship_engine:
                ship_engine.symbol = engine_data.get("symbol", "")
                ship_engine.name = engine_data.get("name", "")
                ship_engine.condition = engine_data.get("condition", 0)
                ship_engine.integrity = engine_data.get("integrity", 0)
                ship_engine.speed = engine_data.get("speed", 0)
                ship_engine.power_required = requirements.get("power", 0)
                ship_engine.crew_required = requirements.get("crew", 0)
                ship_engine.quality = engine_data.get("quality", 0)
            else:
                ship_engine = ShipEngine(
                    ship_id=ship.id,
                    symbol=engine_data.get("symbol", ""),
                    name=engine_data.get("name", ""),
                    condition=engine_data.get("condition", 0),
                    integrity=engine_data.get("integrity", 0),
                    speed=engine_data.get("speed", 0),
                    power_required=requirements.get("power", 0),
                    crew_required=requirements.get("crew", 0),
                    quality=engine_data.get("quality", 0),
                )
                session.add(ship_engine)

            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_ShipCooldown(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return

            cooldown_data = ship_info.get("data", {}).get("cooldown", {})
            if not cooldown_data:
                logger.warning(
                    f"No cooldown data found for ship {self.ship.shipSymbol}."
                )
                return

            ship_cooldown = (
                session.query(ShipCooldown).filter_by(ship_id=ship.id).first()
            )

            if ship_cooldown:
                ship_cooldown.total_seconds = cooldown_data.get("totalSeconds", 0)
                ship_cooldown.remaining_seconds = cooldown_data.get(
                    "remainingSeconds", 0
                )
            else:
                ship_cooldown = ShipCooldown(
                    ship_id=ship.id,
                    total_seconds=cooldown_data.get("totalSeconds", 0),
                    remaining_seconds=cooldown_data.get("remainingSeconds", 0),
                )
                session.add(ship_cooldown)

            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_ShipTelemetry(self, session=None, ship_info=None):
        def core(session, ship_info):
            ship = session.query(Ship).filter_by(symbol=self.ship.shipSymbol).first()
            if not ship:
                logger.warning(f"Ship {self.ship.shipSymbol} not found in DB.")
                return

            data = ship_info.get("data", {})

            # Update or create each subcomponent and get their IDs
            def get_or_create_subcomponent(model, data_key):
                sub_data = data.get(data_key)
                if not sub_data:
                    return None

                # Log the raw data
                logger.debug(
                    f"[DEBUG] Creating or updating {model.__name__} with: {sub_data}"
                )

                # Fix nested dict issue for ShipFuel
                if data_key == "fuel" and isinstance(sub_data.get("consumed"), dict):
                    logger.debug(
                        f"[DEBUG] Fuel consumed before fix: {sub_data['consumed']}"
                    )
                    sub_data["consumed"] = sub_data["consumed"].get("amount", 0)
                    logger.debug(
                        f"[DEBUG] Fuel consumed after fix: {sub_data['consumed']}"
                    )

                obj = session.query(model).filter_by(ship_id=ship.id).first()
                if obj:
                    for key, value in sub_data.items():
                        setattr(obj, key, value)
                else:
                    obj = model(ship_id=ship.id, **sub_data)
                    session.add(obj)

                session.flush()
                return obj.id

            fuel_id = get_or_create_subcomponent(ShipFuel, "fuel")
            cargo_id = get_or_create_subcomponent(ShipCargo, "cargo")
            crew_id = get_or_create_subcomponent(ShipCrew, "crew")
            frame_id = get_or_create_subcomponent(ShipFrame, "frame")
            reactor_id = get_or_create_subcomponent(ShipReactor, "reactor")
            engine_id = get_or_create_subcomponent(ShipEngine, "engine")
            cooldown_id = get_or_create_subcomponent(ShipCooldown, "cooldown")

            # Create new ShipTelemetry record linking the subcomponents
            telemetry = ShipTelemetry(
                ship_id=ship.id,
                timestamp=datetime.utcnow(),
                fuel_id=fuel_id,
                cargo_id=cargo_id,
                crew_id=crew_id,
                frame_id=frame_id,
                reactor_id=reactor_id,
                engine_id=engine_id,
                cooldown_id=cooldown_id,
            )
            session.add(telemetry)
            session.flush()

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )

    def update_all_telemetry_subcomponent(self, session=None, ship_info=None):
        def core(session, ship_info):
            update_tasks = [
                ("ShipFuel", self.update_ShipFuel),
                ("ShipCargo", self.update_ShipCargo),
                ("ShipCrew", self.update_ShipCrew),
                ("ShipFrame", self.update_ShipFrame),
                ("ShipReactor", self.update_ShipReactor),
                ("ShipEngine", self.update_ShipEngine),
                ("ShipCooldown", self.update_ShipCooldown),
                ("ShipNavigation", self.update_ShipNavigation),
                ("ShipTelemetry", self.update_ShipTelemetry),
            ]

            for name, func in update_tasks:
                try:
                    logger.info(f"Updating {name}")
                    func(session=session, ship_info=ship_info)
                    logger.info(f"Finished updating {name}")
                except Exception as e:
                    logger.info(
                        f"Failed to update {name} for ship {self.ship.shipSymbol}: {e}"
                    )

        return self.ship.with_session_and_ship_info(
            session=session, ship_info=ship_info, fn=core
        )


class ShipExporation:
    def __init__(self, ship):
        self.ship = ship
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.ship.shipSymbol}"

    def chart_waypoint(self):
        """Charts the current waypoint, making is's traits visible."""
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/chart", auth_req=True
        )

    def scan_systems(self):
        """Scans the current system for nearby waypoints.
        Sensor Array must be installed on the ship.
        """
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/scan/systems", auth_req=True
        )

    def scan_waypoint(self):
        """Scans a specific waypoint for detailed information.
        Sensor Array must be installed on the ship.
        """
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/scan/waypoints", auth_req=True
        )

    def scan_ships(self):
        """Scans nearby ships for detailed information.
        Sensor Array must be installed on the ship.
        """
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/scan/ships", auth_req=True
        )


class MaintainShip:
    def __init__(self, ship):
        self.ship = ship
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.ship.shipSymbol}"

    def get_scrap_cost(self):
        """Fetches the current scrap amount of the ship."""
        return self.ship._get_request(f"{self.ship.base_ship_url}/scrap", auth_req=True)

    def scrap(self):
        """Scraps the ship, removing it from the game."""
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/scrap", auth_req=True
        )

    def get_repair_cost(self):
        """Fetches the cost to repair the ship."""
        return self.ship._get_request(
            f"{self.ship.base_ship_url}/repair", auth_req=True
        )

    def repair(self):
        """Repairs the ship, restoring its integrity."""
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/repair", auth_req=True
        )

    def get_ship_modules(self):
        """Fetches the modules installed on the ship."""
        return self.ship._get_request(
            f"{self.ship.base_ship_url}/modules", auth_req=True
        )

    def install_module(self, moduleSymbol):
        """Installs a module on the ship."""
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/modules/install",
            data={"symbol": moduleSymbol},
            auth_req=True,
        )

    def remove_ship_module(self, moduleSymbol):
        """Removes a module from the ship."""
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/modules/remove",
            data={"symbol": moduleSymbol},
            auth_req=True,
        )

    def get_ship_mounts(self):
        """Fetches the mounts installed on the ship."""
        return self.ship._get_request(
            f"{self.ship.base_ship_url}/mounts", auth_req=True
        )

    def install_mount(self, mountSymbol):
        """Installs a mount on the ship."""
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/mounts/install",
            data={"symbol": mountSymbol},
            auth_req=True,
        )

    def remove_ship_mount(self, mountSymbol):
        """Removes a mount from the ship."""
        return self.ship._post_request(
            f"{self.ship.base_ship_url}/mounts/remove",
            data={"symbol": mountSymbol},
            auth_req=True,
        )


class ShipResourceOperations:
    def __init__(self, ship):
        self.ship = ship
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.ship.shipSymbol}"

    def extract(self, survey=None):
        data = {"survey": survey} if survey else None
        return self.ship._post_request(
            f"{self.base_ship_url}/extract", data, auth_req=True
        )

    def siphon_resources(self):
        """Siphons resources from the current waypoint.
        Requires siphon mounts and a gas processor installed."""
        return self.ship._post_request(f"{self.base_ship_url}/siphon", auth_req=True)

    def jettison_cargo(self, cargoSymbol, units):
        """Jettisons cargo from the ship's cargo hold."""
        return self.ship._post_request(
            f"{self.base_ship_url}/jettison",
            data={"symbol": cargoSymbol, "units": units},
            auth_req=True,
        )


class ShipTrade:
    def __init__(self, ship):
        self.ship = ship
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.ship.shipSymbol}"

    def purchase(self, product_symbol, units):
        """Purchases a product from the current waypoint's market."""
        return self.ship._post_request(
            f"{self.base_ship_url}/purchase",
            data={"symbol": product_symbol, "units": units},
            auth_req=True,
        )

    def sell(self, product_symbol, units):
        """Sells a product to the current waypoint's market."""
        return self.ship._post_request(
            f"{self.base_ship_url}/sell",
            data={"symbol": product_symbol, "units": units},
            auth_req=True,
        )

    def transfer_cargo_between_ships(self, target_ship_symbol, cargo_symbol, units):
        """Transfers cargo between ships."""
        return self.ship._post_request(
            f"{self.base_ship_url}/transfer",
            data={
                "shipSymbol": target_ship_symbol,
                "tradeSymbol": cargo_symbol,
                "units": units,
            },
            auth_req=True,
        )

    def get_ship_cargo(self):
        """Fetches the current cargo of the ship."""
        return self.ship._get_request(f"{self.base_ship_url}/cargo", auth_req=True)


class ShipAPI:
    def __init__(self, ship):
        self.ship = ship
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.ship.shipSymbol}"

    # 🚀 Ship Status & Information
    def get_ship_status(self):
        """Fetches the current status of the ship, including its location."""
        url = f"{self.base_ship_url}"
        return self.ship._get_request(url, auth_req=True)

    def fetch_market_data_of_current_waypoint(self):
        waypoint = self.ship.waypointSymbol
        system = "-".join(waypoint.split("-")[:2])
        return self.ship.player.fetch_market_data(system, waypoint)

    def fetch_market_data_of_destination_waypoint(self):
        waypoint = self.ship.waypointSymbol
        system = "-".join(waypoint.split("-")[:2])
        return self.ship.player.fetch_market_data(system, waypoint)

    # 🚀 Basic Actions
    def get_in_orbit(self):
        try:
            result = self.ship._post_request(
                f"{self.base_ship_url}/orbit", auth_req=True
            )
            if not result:
                raise ValueError("Orbit request returned no result.")
            self.ship.update_from_api()
            self.ship.save_to_db()
            return result
        except Exception as e:
            logger.error(f"Failed to enter orbit for ship {self.ship.shipSymbol}: {e}")
            return None

    def dock(self):
        return self.ship._post_request(f"{self.base_ship_url}/dock", auth_req=True)

    def change_flight_mode(self, flight_mode):
        return self.ship._patch_request(
            f"{self.base_ship_url}/nav", {"flightMode": flight_mode}, auth_req=True
        )

    def refuel(self, units, fromCargo=False):
        """Refuels the ship using the specified amount of fuel.
        If fromCargo is True, it will use fuel from the ship's cargo hold.
        """
        return self.ship._post_request(
            f"{self.base_ship_url}/refuel",
            data={"units": units, "fromCargo": fromCargo},
            auth_req=True,
        )

    def survey(self):
        return self.ship._post_request(f"{self.base_ship_url}/survey", auth_req=True)

    # 🚀 Travel & Navigation
    def travel_to_waypoint(self, waypointSymbol):
        return self.ship._post_request(
            f"{self.base_ship_url}/navigate",
            {"waypointSymbol": waypointSymbol},
            auth_req=True,
        )

    def warp_to_system(self, waypointSymbol):
        return self.ship._post_request(
            f"{self.base_ship_url}/warp",
            {"systemSymbol": waypointSymbol},
            auth_req=True,
        )

    def jump_to_system(self, waypointSymbol):
        return self.ship._post_request(
            f"{self.base_ship_url}/jump",
            {"systemSymbol": waypointSymbol},
            auth_req=True,
        )


class SpaceShip(BaseAPI):
    def __init__(self, shipSymbol, player=None, agent_token=None):
        if not (player or agent_token):
            raise ValueError("Either player or agent_token must be provided.")

        token = player.agent_token if player else agent_token
        super().__init__(token)

        self.player = player
        self.shipSymbol = shipSymbol
        self.base_ship_url = f"{BASE_URL}/my/ships/{shipSymbol}"

        self.factionSymbol = "Unknown"
        self.role = "Unknown"
        self.status = "Unknown"
        self.flightMode = "Unknown"
        self.systemSymbol = "Unknown"
        self.waypointSymbol = "Unknown"
        self.speed = 0

        self.db = ShipDB(self)
        self.telemetry = Telemetry(self)
        self.api = ShipAPI(self)
        self.exploration = ShipExporation(self)
        self.maintenance = MaintainShip(self)
        self.resource_operations = ShipResourceOperations(self)
        self.trade = ShipTrade(self)

    @classmethod
    def load_or_create(cls, player, shipSymbol, session=None, reload_from_api=False):
        if session is None:
            with get_session() as new_session:
                return cls.load_or_create(
                    player,
                    shipSymbol,
                    session=new_session,
                    reload_from_api=reload_from_api,
                )

        ship = session.query(Ship).filter_by(symbol=shipSymbol).first()
        if ship and not reload_from_api:
            ship_obj = cls(shipSymbol, player=player)
            ship_obj.factionSymbol = ship.factionSymbol
            ship_obj.role = ship.role
            ship_obj.status = ship.status
            ship_obj.flightMode = ship.flightMode
            ship_obj.systemSymbol = ship.systemSymbol
            ship_obj.waypointSymbol = ship.waypointSymbol
            ship_obj.speed = ship.speed
            logger.info(f"Loaded ship {shipSymbol} from DB.")
            return ship_obj

        # Always fetch fresh data and update DB\
        logger.info(f"Updating ship {shipSymbol} from API.")
        ship_obj = cls(shipSymbol, player=player)
        try:
            ship_obj.update_from_api()
            ship_obj.save_to_db(session=session)
            return ship_obj
        except Exception as e:
            logger.error(f"Failed to fetch and save ship {shipSymbol}: {e}")
            raise

    def save_to_db(
        self,
        session=None,
        update_mounts=True,
        update_modules=True,
        update_all_subcomponents=True,
    ):
        if not session:
            with get_session() as new_session:
                self.save_to_db(
                    session=new_session,
                    update_modules=update_modules,
                    update_mounts=update_mounts,
                    update_all_subcomponents=update_all_subcomponents,
                )
                return

        ship = session.query(Ship).filter_by(symbol=self.shipSymbol).first()
        if self.player:
            agent = (
                session.query(Agent)
                .filter_by(agent_token=self.player.agent_token)
                .first()
            )
        else:
            agent = session.query(Agent).filter_by(agent_token=self.agent_token).first()

        if not agent:
            raise ValueError("Associated Agent not found in DB.")

        if not ship:
            ship = Ship(
                agent_id=agent.id,
                symbol=self.shipSymbol,
                factionSymbol=self.factionSymbol,
                role=self.role,
                status=self.status,
                flightMode=self.flightMode,
                systemSymbol=self.systemSymbol,
                waypointSymbol=self.waypointSymbol,
                speed=self.speed,
            )
        else:
            ship.factionSymbol = self.factionSymbol
            ship.role = self.role
            ship.status = self.status
            ship.flightMode = self.flightMode
            ship.systemSymbol = self.systemSymbol
            ship.waypointSymbol = self.waypointSymbol
            ship.speed = self.speed

        session.add(ship)
        session.flush()
        ship_info = self.api.get_ship_status()
        if update_modules:
            self.telemetry.update_modules(session=session, ship_info=ship_info)
        if update_mounts:
            self.telemetry.update_mounts(session=session, ship_info=ship_info)
        if update_all_subcomponents:
            self.telemetry.update_all_telemetry_subcomponent(
                session=session, ship_info=ship_info
            )
        logger.info(f"Saved ship {self.shipSymbol} to DB.")

    def update_from_api(self):
        """Fetches and updates ship info from the API."""
        ship_info = self.api.get_ship_status()["data"]
        if ship_info:
            # Update ship attributes
            self.factionSymbol = ship_info["registration"].get(
                "factionSymbol", "UNKNOWN"
            )
            self.role = ship_info["registration"].get("role", "UNKNOWN")
            self.status = ship_info["nav"].get("status", "UNKNOWN")
            self.flightMode = ship_info["nav"].get("flightMode", "UNKNOWN")
            self.systemSymbol = ship_info["nav"].get("systemSymbol", "UNKNOWN")
            self.waypointSymbol = ship_info["nav"].get("waypointSymbol", "UNKNOWN")
            self.speed = ship_info["engine"].get("speed", 0)

        else:
            logger.warning("Ship data not found from API.")

    def with_session_and_ship_info(self, session=None, ship_info=None, fn=None):
        if fn is None:
            raise ValueError("Function `fn` must be provided.")

        def task(s):
            ship_info_resolved = ship_info or self.api.get_ship_status()
            return fn(s, ship_info_resolved)

        if session:
            return task(session)
        else:
            with get_session() as new_session:
                return task(new_session)

    def __str__(self):
        return (
            f"SpaceShip '{self.shipSymbol}':\n"
            f"  Faction: {self.factionSymbol}\n"
            f"  Role: {self.role}\n"
            f"  Status: {self.status}\n"
            f"  Flight Mode: {self.flightMode}\n"
            f"  Location: System '{self.systemSymbol}', Waypoint '{self.waypointSymbol}'\n"
            f"  Speed: {self.speed} units\n"
            f"  Owned by Player: {self.player.symbol if self.player else 'Unknown'}"
        )
