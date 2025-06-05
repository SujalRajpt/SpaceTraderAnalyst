from src.utils.pretty_print import pretty_print
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.db.db_session import get_session
from src.db.models import Agent, Ship, ShipNavigation
from src.objects.sol_system import SolSystem, SolWaypoints


with get_session() as session:
    agent = session.query(Agent).filter_by(id=1).first()

    if agent:
        agent_token = agent.agent_token
        symbol = agent.symbol
    else:
        agent_token = None


player = Player(symbol)
# ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[0], player=player)

# shipyards = player.fetch_waypoints(filter_by_trait="SHIPYARD")
# ship_data = player.fetch_market_data(waypoint="X1-AB31-H54", market="shipyard")
# pretty_print(ship_data)

# recipt = player.purchase_ship(ship_type="SHIP_MINING_DRONE", waypoint="X1-AB31-H54")
# pretty_print(recipt)

# drone = SpaceShip.load_or_create(player=player, shipSymbol="IRONMAN-3")
# print(drone)


# asteroid = player.fetch_waypoints(filter_by_type="ENGINEERED_ASTEROID")
# pretty_print(asteroid)
# ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[2], player=player)


# ship = SpaceShip.load_or_create(
#     shipSymbol=player.shipSymbols[2], player=player, reload_from_api=True
# )
# ship.api.dock()
# print(ship)

# ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[2], player=player)
# recipt = ship.api.refuel(units=1)
# pretty_print(recipt)

# update fuel
# ship = SpaceShip.load_or_create(
#     shipSymbol=player.shipSymbols[2], player=player, reload_from_api=True
# )


# ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[2], player=player)
# ship.api.get_in_orbit()
# ship = SpaceShip.load_or_create(
#     shipSymbol=player.shipSymbols[2], player=player, reload_from_api=True
# )


ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[0], player=player)

pretty_print(ship.exploration.scan_systems())
# extract_json = ship.resource_operations.extract()
# pretty_print(extract_json)


# bug in cargo
# ship = SpaceShip.load_or_create(
#     shipSymbol=player.shipSymbols[2], player=player, reload_from_api=True
# )
# print(ship.db.fetch_shipcargo_from_db())

# ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[0], player=player)
# pretty_print(ship.api.get_ship_status())
