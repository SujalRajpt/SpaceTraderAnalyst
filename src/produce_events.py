from src.async_tasks.kafka_producer import start_trip_event, start_extract_event
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.db.db_session import get_session
from src.db.models import Agent

with get_session() as session:
    agent = session.query(Agent).filter_by(id=1).first()

    if agent:
        agent_token = agent.agent_token
        symbol = agent.symbol
    else:
        agent_token = None


player = Player(agent_token)
ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[2], player=player)
destination_waypoint = "X1-AB31-A1"


start_trip_event(
    player_token=agent_token,
    destination_waypoint=destination_waypoint,
    shipsymbol=ship.shipSymbol,
)

# start_extract_event(
#     player_token=agent_token,
#     shipsymbol=ship.shipSymbol,
# )
