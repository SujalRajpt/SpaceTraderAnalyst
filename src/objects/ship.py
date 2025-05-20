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

    @classmethod
    def load_or_create(cls, player, shipSymbol, session=None):
        if session is None:
            with get_session() as new_session:
                return cls.load_or_create(player, shipSymbol, session=new_session)

        ship_obj = cls(shipSymbol, player=player)
        ship = session.query(Ship).filter_by(symbol=shipSymbol).first()
        if ship:
            # Load from DB

            ship_obj.factionSymbol = ship.factionSymbol
            ship_obj.role = ship.role
            ship_obj.status = ship.status
            ship_obj.flightMode = ship.flightMode
            ship_obj.systemSymbol = ship.systemSymbol
            ship_obj.waypointSymbol = ship.waypointSymbol
            ship_obj.speed = ship.speed
            logger.info(f"Loaded ship {shipSymbol} from DB.")
        else:
            # Fetch from API and save
            logger.info(f"Ship {shipSymbol} not found in DB. Fetching from API.")
            ship_obj.update_from_api()
            ship_obj.save_to_db(session=session)

        return ship_obj

    def save_to_db(self, session):
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

    def update_from_api(self):
        """Fetches and updates ship info from the API."""
        ship_info = self.get_ship_status()["data"]
        if ship_info:
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

    # 🚀 Ship Status & Information
    def get_ship_status(self):
        """Fetches the current status of the ship, including its location."""
        url = f"{self.base_ship_url}"
        return self._get_request(url, auth_req=True)

    def fetch_market_data_of_current_waypoint(self):
        waypoint = self.waypointSymbol
        system = "-".join(waypoint.split("-")[:2])
        return self.player.fetch_market_data(system, waypoint)

    def fetch_market_data_of_destination_waypoint(self):
        waypoint = self.waypointSymbol
        system = "-".join(waypoint.split("-")[:2])
        return self.player.fetch_market_data(system, waypoint)

    # 🚀 Basic Actions
    def get_in_orbit(self):
        return self._post_request(f"{self.base_ship_url}/orbit", auth_req=True)

    def dock(self):
        return self._post_request(f"{self.base_ship_url}/dock", auth_req=True)

    def change_flight_mode(self, flight_mode):
        return self._patch_request(
            f"{self.base_ship_url}/nav", {"flightMode": flight_mode}, auth_req=True
        )

    def refuel(self):
        return self._post_request(
            f"{self.base_ship_url}/refuel", {"fromCargo": True}, auth_req=True
        )

    def extract(self, survey=None):
        data = {"survey": survey} if survey else None
        return self._post_request(f"{self.base_ship_url}/extract", data, auth_req=True)

    def survey(self):
        return self._post_request(f"{self.base_ship_url}/survey", auth_req=True)

    # 🚀 Travel & Navigation
    def travel_to_waypoint(self, waypointSymbol):
        self.status = "Moving"
        self.destination = waypointSymbol
        return self._post_request(
            f"{self.base_ship_url}/navigate",
            {"waypointSymbol": waypointSymbol},
            auth_req=True,
        )

    def warp_to_system(self, waypointSymbol):
        self.status = "Moving"
        self.destination = waypointSymbol
        return self._post_request(
            f"{self.base_ship_url}/warp",
            {"systemSymbol": waypointSymbol},
            auth_req=True,
        )

    def jump_to_system(self, waypointSymbol):
        self.status = "Moving"
        self.destination = waypointSymbol
        return self._post_request(
            f"{self.base_ship_url}/jump",
            {"systemSymbol": waypointSymbol},
            auth_req=True,
        )

    # 🚀 Repair & Scrapping
    def repair_ship(self):
        return self._post_request(f"{self.base_ship_url}/repair", auth_req=True)

    def get_repair_estimate(self):
        return self._get_request(f"{self.base_ship_url}/repair", auth_req=True)

    def scrap_ship(self):
        return self._post_request(f"{self.base_ship_url}/scrap", auth_req=True)

    def get_scrap_estimate(self):
        return self._get_request(f"{self.base_ship_url}/scrap", auth_req=True)
