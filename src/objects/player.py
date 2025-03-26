import requests
from src.utils.config import BASE_URL, acc_token
from src.utils.logger import logger
from src.api.base_api import BaseAPI
from src.db.db_session import get_session
from src.db.models import Agent, Ship


class Player(BaseAPI):
    """Handles agent (player) actions in SpaceTraders."""

    def __init__(self, agent_token: str, load_from_db=True) -> None:
        super().__init__(agent_token)
        self.agent_token = agent_token
        self.current_system = "UNKNOWN"
        self.current_waypoint = "UNKNOWN"
        self.credit = 0
        self.starting_faction = "UNKNOWN"
        self.shipSymbol = []
        if load_from_db:
            self.load_from_db()

    @staticmethod
    def create_player(symbol: str, faction: str = "COSMIC"):
        url = f"{BASE_URL}/register"
        headers = {
            "Authorization": f"Bearer {acc_token}",
            "Content-Type": "application/json",
        }

        data = {"symbol": symbol, "faction": faction}

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            token = response_data.get("data", {}).get("token")

            if not token:
                logger.error("Failed to retrieve player token from response.")
                return None

            logger.info(f"Player '{symbol}' registered successfully.")
            player = Player(token, load_from_db=False)
            player.update_from_api()
            player.save_to_db()
            return player

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to register player: {e}")
            return None

    def fetch_agent_info(self):
        """Fetches the agent's details, including current system and waypoint."""
        url = f"{BASE_URL}/my/agent"
        try:
            response = self._get_request(url)
            return response.get("data", {}) if response else {}
        except Exception as e:
            logger.error(f"Failed to fetch agent info: {e}")
            return {}

    def update_from_api(self):
        """Updates the player's current system (e.g., after traveling)."""
        agent_info = self.fetch_agent_info()
        headquarters = agent_info.get("headquarters", "")

        if headquarters:
            self.current_system = "-".join(headquarters.split("-")[:2])
            self.current_waypoint = headquarters
            self.credit = agent_info.get("credits", 0)
            self.starting_faction = agent_info.get("startingFaction", "UNKNOWN")
            ships_data = self.view_my_ships()
            self.shipSymbols = (
                [x["symbol"] for x in ships_data.get("data", [])] if ships_data else []
            )

        else:
            logger.warning("Player no longer exists !!")

    def save_to_db(self):
        """Saves player data to the database."""
        with get_session() as session:
            agent = session.query(Agent).filter_by(agent_token=self.agent_token).first()
            if agent:
                agent.current_system = self.current_system
                agent.current_waypoint = self.current_waypoint
                agent.credit = self.credit
                agent.starting_faction = self.starting_faction
            else:
                agent = Agent(
                    agent_token=self.agent_token,
                    current_system=self.current_system,
                    current_waypoint=self.current_waypoint,
                    credit=self.credit,
                    starting_faction=self.starting_faction,
                )
            session.add(agent)
            session.flush()

            for shipSymbol in self.shipSymbols:
                # Avoid duplicate ship insertion
                if not session.query(Ship).filter_by(symbol=shipSymbol).first():
                    session.add(Ship(agent_id=agent.id, symbol=shipSymbol))

    def load_from_db(self):
        with get_session() as session:
            agent = session.query(Agent).filter_by(agent_token=self.agent_token).first()
            if agent:
                self.current_system = agent.current_system
                self.current_waypoint = agent.current_waypoint
                self.credit = agent.credit
                self.starting_faction = agent.starting_faction
                self.shipSymbol = [
                    ship.symbol
                    for ship in session.query(Ship).filter_by(agent_id=agent.id).all()
                ]
            else:
                logger.warning("Player not found in database.")

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

    def fetch_current_waypoint_info(self):
        """Fetches market data for a specific waypoint."""
        if self.current_system == "UNKNOWN":
            logger.error("Cannot fetch waypoint info: Current system is unknown.")
            return None

        url = f"{BASE_URL}/systems/{self.current_system}/waypoints/{self.current_waypoint}/market"
        return self._get_request(
            url, auth_req=True
        )  # Changed to True for market access

    def view_my_ships(self):
        """Fetches all player-owned ships."""
        url = f"{BASE_URL}/my/ships"
        return self._get_request(url)
