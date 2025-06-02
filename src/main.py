from src.utils.pretty_print import pretty_print
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.objects.market import Market
from src.db.db_session import get_session
from src.db.models import Agent, Ship, ShipNavigation
from src.objects.sol_system import SolSystem


with get_session() as session:
    agent = session.query(Agent).filter_by(id=1).first()

    if agent:
        agent_token = agent.agent_token
        symbol = agent.symbol
    else:
        agent_token = None


player = Player(agent_token=agent_token)
ship = SpaceShip.load_or_create(
    shipSymbol=player.shipSymbols[0], player=player, reload_from_api=True
)
ship2 = SpaceShip.load_or_create(
    shipSymbol=player.shipSymbols[1], player=player, reload_from_api=True
)
print(ship)
print(ship2)
# nav = ship.fetch_navigation_info_from_db()
# origin_system = nav["origin_system"]

# sol = SolSystem(origin_system)
# waypoints = sol.get_waypoints()

# # Calculate distances to all waypoints
# distances = []
# for wp in waypoints:
#     waypoint_symbol = wp["waypoint_symbol"]
#     distance = ship.get_distance_to_waypoint(destination_waypoint=waypoint_symbol)
#     distances.append((waypoint_symbol, distance))

# # Sort by distance
# sorted_distances = sorted(distances, key=lambda x: x[1])

# # Pretty print
# for symbol, dist in sorted_distances:
#     print(f"{symbol}: {dist:.2f} units")
