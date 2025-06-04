import requests
from src.utils.config import BASE_URL, acc_token
from src.utils.logger import logger
from src.api.base_api import BaseAPI
from src.db.db_session import get_session
from src.db.models import Agent, Ship
from src.objects.ship import SpaceShip


class PlayerContract:
    """Handles player contracts in SpaceTraders."""

    def __init__(self, player: "Player"):
        self.player = player

    def view_contracts(self):
        """Fetches agent's active contracts."""
        url = f"{BASE_URL}/my/contracts"
        return self.player._get_request(url)

    def accept_contract(self, contract_id):
        """Accepts a contract."""
        url = f"{BASE_URL}/my/contracts/{contract_id}/accept"
        return self.player._post_request(url)

    def fulfill_contract(self, contract_id):
        """Fulfills a contract."""
        url = f"{BASE_URL}/my/contracts/{contract_id}/fulfill"
        return self.player._post_request(url)

    def deliver_cargo_of_contract(self, contract_id, shipSymbol, tradeSymbol, units):
        """Delivers cargo for a contract. ship must be at the delivery location"""
        url = f"{BASE_URL}/my/contracts/{contract_id}/deliver"
        data = {"shipSymbol": shipSymbol, "tradeSymbol": tradeSymbol, "units": units}
        return self.player._post_request(url, data=data)

    def negotiate_contract(self, contract_id):
        """
        Negotiate a contract with a faction.

        An agent can only have one active or offered contract at a time.
        To negotiate, the ship must be at a waypoint with a faction present.
        Once negotiated, the contract is added to the agent's offered contracts.
        """
        url = f"{BASE_URL}/my/contracts/{contract_id}/negotiate"
        return self.player._post_request(url)


class Player(BaseAPI):
    """Handles agent (player) actions in SpaceTraders."""

    # 1️⃣ Initialization
    def __init__(self, identifier: str, load_from_db: bool = True) -> None:
        """
        Initialize a Player using either symbol or agent_token.

        Args:
            identifier (str): Player symbol or agent token.
            load_from_db (bool): If True, attempt to load from database.
        """
        self.agent_token = None
        self.symbol = None
        self.current_system = "UNKNOWN"
        self.current_waypoint = "UNKNOWN"
        self.credit = 0
        self.starting_faction = "UNKNOWN"
        self.shipSymbols = []

        self.contract = PlayerContract(self)

        if load_from_db:
            self.load_from_db(identifier)

        # Initialize BaseAPI only if token is available
        if self.agent_token:
            super().__init__(self.agent_token)

    def __str__(self):
        return (
            f"🪪 Symbol: {self.symbol}\n"
            f"🚀 Ships: {self.shipSymbols}\n"
            f"🌍 System: {self.current_system}\n"
            f"📍 Waypoint: {self.current_waypoint}\n"
            f"💰 Credit: {self.credit}\n"
            f"🏴 Faction: {self.starting_faction}"
        )

    # 2️⃣ Player Creation
    @staticmethod
    def create_player(symbol: str, faction: str = "COSMIC"):
        """Register a new player using a unique symbol and save to DB."""
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

            agent_token = response_data.get("data", {}).get("token")
            if not agent_token:
                logger.error(
                    "Failed to retrieve agent token from registration response."
                )
                return None

            logger.info(f"Player '{symbol}' registered successfully.")
            player = Player(agent_token, load_from_db=False)
            player.symbol = symbol
            player.agent_token = agent_token
            player.update_from_api()
            player.save_to_db()
            return player

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to register player: {e}")
            return None

    # 3️⃣ API Interactions
    def fetch_agent_info(self):
        """Get agent info from API."""
        url = f"{BASE_URL}/my/agent"
        try:
            response = self._get_request(url)
            return response.get("data", {}) if response else {}
        except Exception as e:
            logger.error(f"Failed to fetch agent info: {e}")
            return {}

    def update_from_api(self):
        """Update local player info from API."""
        agent_info = self.fetch_agent_info()
        headquarters = agent_info.get("headquarters", "")

        if headquarters:
            self.current_system = "-".join(headquarters.split("-")[:2])
            self.current_waypoint = headquarters
            self.credit = agent_info.get("credits", 0)
            self.starting_faction = agent_info.get("startingFaction", "UNKNOWN")
            self.symbol = agent_info.get("symbol", self.symbol)

            ships_data = self.view_my_ships()
            self.shipSymbols = (
                [x["symbol"] for x in ships_data.get("data", [])] if ships_data else []
            )
        else:
            logger.warning("Agent may no longer exist.")

    # 4️⃣ Database Persistence
    def save_to_db(self):
        """Save player and ships to database."""
        with get_session() as session:
            agent = session.query(Agent).filter_by(agent_token=self.agent_token).first()
            if agent:
                agent.current_system = self.current_system
                agent.current_waypoint = self.current_waypoint
                agent.credit = self.credit
                agent.starting_faction = self.starting_faction
            else:
                agent = Agent(
                    symbol=self.symbol,
                    agent_token=self.agent_token,
                    current_system=self.current_system,
                    current_waypoint=self.current_waypoint,
                    credit=self.credit,
                    starting_faction=self.starting_faction,
                )
                session.add(agent)

            session.flush()  # Ensure agent.id is available
            logger.debug(f"Agent saved with ID: {agent.id}")

            for shipSymbol in self.shipSymbols:
                SpaceShip.load_or_create(
                    player=self, shipSymbol=shipSymbol, session=session
                )

    def load_from_db(self, identifier: str):
        """
        Load player data using symbol or agent_token.

        Args:
            identifier (str): Either symbol or agent_token.
        """
        with get_session() as session:
            agent = (
                session.query(Agent)
                .filter(
                    (Agent.symbol == identifier) | (Agent.agent_token == identifier)
                )
                .first()
            )

            if agent:
                self.symbol = agent.symbol
                self.agent_token = agent.agent_token
                self.current_system = agent.current_system
                self.current_waypoint = agent.current_waypoint
                self.credit = agent.credit
                self.starting_faction = agent.starting_faction
                self.shipSymbols = [
                    ship.symbol
                    for ship in session.query(Ship).filter_by(agent_id=agent.id).all()
                ]
                logger.info(f"Loaded player '{self.symbol}' from DB.")
            else:
                logger.warning(f"No player found in DB for identifier: {identifier}")

    # 4️⃣ API Request Methods
    def view_factions(self):
        """Fetches all available factions."""
        url = f"{BASE_URL}/factions"
        return self._get_request(url)

    def get_recent_events(self):
        url = f"{BASE_URL}/my/events"
        return self._get_request(url, auth_req=True)

    def view_all_systems(self, params=None):
        """Fetches all available systems."""
        url = f"{BASE_URL}/systems"
        return self._get_request(url, params=params)

    def fetch_waypoints(
        self, current_system=None, filter_by_trait="", filter_by_type=""
    ):
        """Fetches waypoints in the player's current system, optionally filtering by trait."""
        current_system = current_system or self.current_system
        if not current_system:
            logger.error("Cannot fetch waypoints: Current system is unknown.")
            return None
        if filter_by_trait:
            query_params = f"?traits={filter_by_trait}" if filter_by_trait else ""
        elif filter_by_type:
            query_params = f"?type={filter_by_type}" if filter_by_type else ""
        url = f"{BASE_URL}/systems/{current_system}/waypoints{query_params}"
        return self._get_request(url, auth_req=False)

    def fetch_market_data(self, waypoint=None, market="market"):
        """Fetches market data from a given system and waypoint. Change market to shipyard to get shipyard data"""
        waypoint = waypoint or self.current_waypoint

        if not waypoint:
            logger.error("Cannot fetch market data: System or waypoint is unknown.")
            return None
        system = "-".join(waypoint.split("-")[:2])

        url = f"{BASE_URL}/systems/{system}/waypoints/{waypoint}/{market}"
        return self._get_request(url, auth_req=True)

    def view_my_ships(self):
        """Fetches all player-owned ships."""
        url = f"{BASE_URL}/my/ships"
        return self._get_request(url)

    def purchase_ship(self, ship_type: str, waypoint: str):
        """Purchases a ship of the specified type at the given waypoint."""
        url = f"{BASE_URL}/my/ships"
        data = {"shipType": ship_type, "waypointSymbol": waypoint}
        return self._post_request(url, data=data)
