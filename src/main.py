from src.utils.pretty_print import pretty_print
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.objects.market import Market
from src.db.db_session import get_session
from src.db.models import Agent, Ship
from src.objects.sol_system import SolSystem


with get_session() as session:
    agent = session.query(Agent).filter_by(id=1).first()

    if agent:
        agent_token = agent.agent_token
        symbol = agent.symbol
    else:
        agent_token = None


player = Player(agent_token=agent_token)
print(player.shipSymbols)
ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[0], player=player)
print(ship)

# print(player)
# print("" * 20)
# print(ship)

# print(ship.origin)
# origin_system = "-".join(ship.origin.split("-")[:2])
# sol = SolSystem(origin_system)
# neighbors = sol.get_neighbors_within_radius(radius=1000)

# mk = player.fetch_market_data()
# pretty_print(ship.get_ship_status())
