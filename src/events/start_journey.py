import json
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.db.db_session import get_session
from src.db.models import Agent, Ship


def pretty_print(data):
    """Formats and prints JSON data in a readable way."""
    print(json.dumps(data, indent=4))


with get_session() as session:
    agent = session.query(Agent).filter_by(id=1).first()

    if agent:
        agent_token = agent.agent_token
        symbol = agent.symbol
    else:
        agent_token = None


player = Player(agent_token=agent_token)
# print(player.shipSymbols)
ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[0], player=player)
# print(ship)


ship_modules = ship.fetch_shipcooldown_from_db()
pretty_print(ship_modules)
