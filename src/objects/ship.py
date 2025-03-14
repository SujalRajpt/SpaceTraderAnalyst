from src.utils.config import BASE_URL
from src.objects.base_api import BaseAPI


class Ship(BaseAPI):
    def __init__(self, player, shipSymbol):
        super().__init__(player.agent_token)
        self.player = player
        self.shipSymbol = shipSymbol

    def get_in_orbit(self):
        url = f"{BASE_URL}/my/ships/{self.shipSymbol}/orbit"
        return self._post_request(url, auth_req=True)

    def dock(self):
        url = f"{BASE_URL}/my/ships/{self.shipSymbol}/dock"
        return self._post_request(url, auth_req=True)
