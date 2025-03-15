from src.utils.config import BASE_URL
from src.api.base_api import BaseAPI


class Ship(BaseAPI):
    def __init__(self, player, shipSymbol):
        super().__init__(player.agent_token)
        self.player = player
        self.shipSymbol = shipSymbol
        self.base_ship_url = f"{BASE_URL}/my/ships/{self.shipSymbol}"

    def get_in_orbit(self):
        return self._post_request(f"{self.base_ship_url}/orbit", auth_req=True)

    def dock(self):
        return self._post_request(f"{self.base_ship_url}/dock", auth_req=True)

    def change_flight_mode(self, flight_mode):
        return self._patch_request(
            f"{self.base_ship_url}/nav", {"flightMode": flight_mode}, auth_req=True
        )

    def travel_to_waypoint(self, waypointSymbol):
        self.player.update_current_system()
        return self._post_request(
            f"{self.base_ship_url}/navigate",
            {"waypointSymbol": waypointSymbol},
            auth_req=True,
        )

    def warp_to_system(self, systemSymbol):
        self.player.update_current_system()
        return self._post_request(
            f"{self.base_ship_url}/warp", {"systemSymbol": systemSymbol}, auth_req=True
        )

    def jump_to_system(self, systemSymbol):
        self.player.update_current_system()
        return self._post_request(
            f"{self.base_ship_url}/jump", {"systemSymbol": systemSymbol}, auth_req=True
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

    def repair_ship(self):
        return self._post_request(f"{self.base_ship_url}/repair", auth_req=True)

    def get_repair_estimate(self):
        return self._get_request(f"{self.base_ship_url}/repair", auth_req=True)

    def scrap_ship(self):
        return self._post_request(f"{self.base_ship_url}/scrap", auth_req=True)

    def get_scrap_estimate(self):
        return self._get_request(f"{self.base_ship_url}/scrap", auth_req=True)
