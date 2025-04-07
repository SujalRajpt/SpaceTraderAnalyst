import json
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.db.db_session import get_session
from src.db.models import Agent, Waypoint, System
from src.objects.sol_system import SolSystem
from src.utils.logger import logger
from src.objects.market import Market


def pretty_print(data):
    """Formats and prints JSON data in a readable way."""
    print(json.dumps(data, indent=4))


with get_session() as session:
    agent = session.query(Agent).filter_by(id=1).first()

    if agent:
        agent_token = agent.agent_token
        player = Player(agent_token)
        market_builder = Market(player)
    else:
        agent_token = None


market_builder.build_local_market()
# X1-FT7-A1
