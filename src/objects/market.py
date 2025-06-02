import math
import time
from sqlalchemy.exc import IntegrityError
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from src.objects.ship import SpaceShip
from src.objects.sol_system import SolSystem
from src.db.db_session import get_session
from src.db.models import System, Waypoint, MarketTradeGoods, Ship
from src.utils.logger import logger


class Market:
    def __init__(self, player):
        self.player = player

    def build_database(self, limit=10):
        max_pages = self.get_max_pages(limit)
        for page in range(1, max_pages + 1):
            logger.info(f"Fetching page {page}/{max_pages}")
            params = {"page": page, "limit": limit}
            data = self.fetch_with_retries(params)

            if data is None:
                logger.error(f"API failed. Skipping page {page}.")
                break

            systems = data.get("data", [])
            if not systems:
                logger.warning(f"No systems found on page {page}. Stopping.")
                break

            self.store_systems_and_waypoints(systems)

    def fetch_with_retries(self, params, max_retries=3):
        for attempt in range(1, max_retries + 1):
            try:
                response = self.player.view_all_systems(params=params)
                if response:
                    return response
            except Exception as e:
                logger.error(f"API error: {e}")
            logger.warning(f"Retrying ({attempt}/{max_retries})...")
            time.sleep(2)

        logger.error("API failed after maximum retries.")
        return None

    def get_max_pages(self, limit):
        try:
            response = self.player.view_all_systems()
            total = response.get("meta", {}).get("total", 0)
            return math.ceil(total / limit) if total > 0 else 1
        except Exception as e:
            logger.error(f"Failed to get max pages: {e}")
            return 1

    def store_systems_and_waypoints(self, systems):
        with get_session() as session:
            system_map = self.insert_systems(systems, session)
            waypoint_map = self.insert_waypoints(systems, session, system_map)
            self.link_parent_waypoints(systems, session, waypoint_map)
            logger.info("All systems and waypoints stored successfully.")

    def insert_systems(self, systems, session):
        system_map = {}
        for system in systems:
            symbol = system["symbol"]
            existing = session.query(System).filter_by(symbol=symbol).first()
            if existing:
                system_map[symbol] = existing
                continue

            try:
                system_obj = System(
                    symbol=symbol,
                    constellation=system.get("constellation", "UNKNOWN"),
                    name=system.get("name", "UNKNOWN"),
                    sector_symbol=system.get("sectorSymbol", "UNKNOWN"),
                    location=from_shape(
                        Point(system.get("x", 0), system.get("y", 0)), srid=0
                    ),
                )
                session.add(system_obj)
                session.flush()
                system_map[symbol] = system_obj
            except IntegrityError as e:
                logger.error(f"Integrity error on system {symbol}: {e}")
                session.rollback()
        session.commit()
        return system_map

    def insert_waypoints(self, systems, session, system_map):
        waypoint_map = {}
        for system in systems:
            sys_obj = system_map[system["symbol"]]
            for wp in system.get("waypoints", []):
                wp_symbol = wp["symbol"]
                if wp_symbol in waypoint_map:
                    continue
                try:
                    wp_obj = Waypoint(
                        waypoint_symbol=wp_symbol,
                        waypoint_type=wp["type"],
                        waypoint_location=from_shape(Point(wp["x"], wp["y"]), srid=0),
                        system_id=sys_obj.id,
                        parent_waypoint_id=None,
                    )
                    session.add(wp_obj)
                    waypoint_map[wp_symbol] = wp_obj
                except IntegrityError as e:
                    logger.error(f"Integrity error on waypoint {wp_symbol}: {e}")
                    session.rollback()
        session.commit()
        return waypoint_map

    def link_parent_waypoints(self, systems, session, waypoint_map):
        for system in systems:
            for wp in system.get("waypoints", []):
                wp_obj = waypoint_map.get(wp["symbol"])
                parent_symbol = wp.get("orbits")
                if wp_obj and parent_symbol:
                    parent_obj = waypoint_map.get(parent_symbol)
                    if parent_obj:
                        wp_obj.parent_waypoint_id = parent_obj.id
        session.commit()

    def classify_demand(self, sell_price: float, purchase_price: float) -> str:
        if purchase_price == 0:
            return "UNKNOWN"

        ratio = sell_price / purchase_price
        if ratio < 1.1:
            return "LOW"
        elif ratio < 1.3:
            return "MEDIUM"
        elif ratio < 1.5:
            return "HIGH"
        return "VERY_HIGH"

    def save_local_market_to_db(
        self, market_json, ship_id: int, waypoint_id: int
    ) -> None:
        trade_goods = market_json.get("data", {}).get("tradeGoods", [])
        with get_session() as session:
            for item in trade_goods:
                symbol = item.get("symbol", "UNKNOWN")
                entry = (
                    session.query(MarketTradeGoods)
                    .filter_by(
                        ship_id=ship_id, waypoint_id=waypoint_id, product_symbol=symbol
                    )
                    .first()
                )

                if entry:
                    entry.trade_volume = item.get("tradeVolume", "UNKNOWN")
                    entry.type = item.get("type", "UNKNOWN")
                    entry.supply = item.get("supply", "UNKNOWN")
                    entry.activity = item.get("activity", "UNKNOWN")
                    entry.purchase_price = item.get("purchasePrice", "UNKNOWN")
                    entry.sell_price = item.get("sellPrice", "UNKNOWN")
                    entry.demand = self.classify_demand(
                        entry.sell_price, entry.purchase_price
                    )
                else:
                    new_entry = MarketTradeGoods(
                        ship_id=ship_id,
                        waypoint_id=waypoint_id,
                        product_symbol=symbol,
                        trade_volume=item.get("tradeVolume", "UNKNOWN"),
                        type=item.get("type", "UNKNOWN"),
                        supply=item.get("supply", "UNKNOWN"),
                        activity=item.get("activity", "UNKNOWN"),
                        purchase_price=item.get("purchasePrice", "UNKNOWN"),
                        sell_price=item.get("sellPrice", "UNKNOWN"),
                        demand=self.classify_demand(
                            item.get("sellPrice", 0), item.get("purchasePrice", 0)
                        ),
                    )
                    session.add(new_entry)

            session.commit()

    def build_local_market(self, ship_symbols=None):
        if not ship_symbols:
            ship_symbols = self.player.shipSymbols

        for ship_symbol in ship_symbols:
            curr_ship = SpaceShip(self.player, ship_symbol)
            ship_origin_system = curr_ship.waypointSymbol
            sol = SolSystem(ship_origin_system)
            neighbors = sol.get_neighbors_within_radius(radius=1000)

            with get_session() as session:
                ship_record = session.query(Ship).filter_by(symbol=ship_symbol).first()
                for curr_system in neighbors:
                    system_symbol = (
                        curr_system["symbol"]
                        if isinstance(curr_system, dict)
                        else curr_system
                    )
                    system = (
                        session.query(System).filter_by(symbol=system_symbol).first()
                    )

                    if not system:
                        logger.warning(f"No system found with symbol {system_symbol}")
                        continue

                    waypoints = (
                        session.query(Waypoint).filter_by(system_id=system.id).all()
                    )
                    for wp in waypoints:
                        try:
                            market_data = self.player.fetch_market_data(
                                wp.waypoint_symbol
                            )
                            if market_data:
                                self.save_local_market_to_db(
                                    market_json=market_data,
                                    ship_id=ship_record.id,
                                    waypoint_id=wp.id,
                                )
                            else:
                                logger.warning(
                                    f"Market data unavailable for {wp.waypoint_symbol} in {system_symbol}"
                                )
                        except Exception as e:
                            logger.error(
                                f"Exception fetching market data for {wp.waypoint_symbol} in {system_symbol}: {e}"
                            )
