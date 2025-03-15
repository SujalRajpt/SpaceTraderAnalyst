import requests
from src.utils.config import BASE_URL, acc_token
from src.utils.logger import logger
from src.api.base_api import BaseAPI


class PlayerCreator:
    """Handles player creation in SpaceTraders."""

    @classmethod
    def create_player(cls, symbol: str, faction: str = "COSMIC"):
        url = f"{BASE_URL}/register"
        headers = {
            "Authorization": f"Bearer {acc_token}",
            "Content-Type": "application/json",
        }
        data = {"symbol": symbol, "faction": faction}

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raises error for 4xx/5xx status codes
            response_data = response.json()

            logger.info(f"Player '{symbol}' registered successfully.")
            return response_data  # Includes agent token and details

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to register player: {e}")
            return None


class Player(BaseAPI):
    """Handles agent (player) actions in SpaceTraders."""

    def __init__(self, agent_token: str) -> None:
        super().__init__(agent_token)
        self.agent_info = {}
        self.current_system = "UNKNOWN"  # Default to prevent errors

        self.update_current_system()  # Fetch latest system on init

    def fetch_agent_info(self):
        """Fetches the agent's details, including current system and waypoint."""
        url = f"{BASE_URL}/my/agent"
        try:
            response = self._get_request(url)
            return response.get("data", {}) if response else {}
        except Exception as e:
            logger.error(f"Failed to fetch agent info: {e}")
            return {}

    def update_current_system(self):
        """Updates the player's current system (e.g., after traveling)."""
        agent_info = self.fetch_agent_info()
        headquarters = agent_info.get("headquarters", "")

        if headquarters:
            self.current_system = "-".join(headquarters.split("-")[:2])
        else:
            logger.warning("Headquarters not found, keeping previous system.")

        self.agent_info = agent_info

    def view_factions(self):
        """Fetches all available factions."""
        url = f"{BASE_URL}/factions"
        return self._get_request(url)

    def view_contracts(self):
        """Fetch agent's active contracts."""
        url = f"{BASE_URL}/my/contracts"
        return self._get_request(url)

    def accept_contract(self, contract_id):
        url = f"{BASE_URL}/my/contracts/{contract_id}/accept"
        return self._post_request(url)

    def view_all_systems(self):
        url = f"{BASE_URL}/systems"
        return self._get_request(url)

    def fetch_waypoints(self, filter_by_trait=""):
        """Fetches waypoints in the player's current system, optionally filtering by trait."""
        if self.current_system == "UNKNOWN":
            logger.error("Cannot fetch waypoints: Current system is unknown.")
            return None

        query_params = f"?traits={filter_by_trait}" if filter_by_trait else ""
        url = f"{BASE_URL}/systems/{self.current_system}/waypoints{query_params}"
        return self._get_request(url, auth_req=False)

    def fetch_waypoint_info(self, waypoint_symbol):
        """Fetches market data for a specific waypoint."""
        if self.current_system == "UNKNOWN":
            logger.error("Cannot fetch waypoint info: Current system is unknown.")
            return None

        url = f"{BASE_URL}/systems/{self.current_system}/waypoints/{waypoint_symbol}/market"
        return self._get_request(
            url, auth_req=True
        )  # Changed to True for market access

    def view_my_ships(self):
        """Fetches all player-owned ships."""
        url = f"{BASE_URL}/my/ships"
        return self._get_request(url)
