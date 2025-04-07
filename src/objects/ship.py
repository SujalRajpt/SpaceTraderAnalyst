from src.utils.config import BASE_URL
from src.api.base_api import BaseAPI


class SpaceShip(BaseAPI):
    def __init__(self, player, shipSymbol):
        super().__init__(player.agent_token)
        self.player = player
        self.shipSymbol = shipSymbol
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.shipSymbol}"
        self.origin = "Unknown"
        self.destination = "Unknown"
        self.arrival_time = "Unknown"
        self.departure_time = "Unknown"
        self.cache_ship_info()
        self.status = "Stalled" if self.origin == self.destination else "Moving"

    def cache_ship_info(self):
        try:
            route = (
                self.get_ship_status().get("data", {}).get("nav", {}).get("route", {})
            )
        except Exception as e:
            print(f"Error fetching ship status: {e}")
            return
        self.origin = route.get("origin", {}).get("symbol")
        self.destination = route.get("destination", {}).get("symbol")
        self.arrival_time = route.get("arrival")
        self.departure_time = route.get("departureTime")

    def __str__(self):
        return (
            f"🚀 Ship: {self.shipSymbol}\n"
            f"🌍 Origin System: {self.origin}\n"
            f"📍 Destination System: {self.destination}\n"
            f"⏳ Departure Time: {self.departure_time}\n"
            f"🛬 Arrival Time: {self.arrival_time}"
        )

    # 🚀 Ship Status & Information
    def get_ship_status(self):
        """Fetches the current status of the ship, including its location."""
        url = f"{self.base_ship_url}"
        return self._get_request(url, auth_req=True)

    def fetch_market_data_of_current_waypoint(self):
        waypoint = self.origin
        system = "-".join(waypoint.split("-")[:2])
        return self.player.fetch_market_data(system, waypoint)

    def fetch_market_data_of_destination_waypoint(self):
        waypoint = self.destination
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
