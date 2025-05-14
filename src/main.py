import json
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.objects.market import Market
from src.db.db_session import get_session
from src.db.models import Agent, Ship
from src.objects.sol_system import SolSystem


def pretty_print(data):
    """Formats and prints JSON data in a readable way."""
    print(json.dumps(data, indent=4))


with get_session() as session:
    agent = session.query(Agent).filter_by(id=2).first()

    if agent:
        agent_token = agent.agent_token
    else:
        agent_token = None


player = Player(agent_token)
ship = SpaceShip(player, "AARNAV-1")

# print(player)
# print("" * 20)
# print(ship)

# print(ship.origin)
origin_system = "-".join(ship.origin.split("-")[:2])
sol = SolSystem(origin_system)
neighbors = sol.get_neighbors_within_radius(radius=1000)

mk = player.fetch_market_data()
pretty_print(mk)
