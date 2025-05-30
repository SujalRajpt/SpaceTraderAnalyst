from src.async_tasks.kafka_producer import start_trip_event
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


player = Player(agent_token=agent_token)
ship = SpaceShip.load_or_create(shipSymbol=player.shipSymbols[1], player=player)
destination_waypoint = "X1-GP53-FZ5A"
destination_waypoint2 = "X1-GP53-H55"

start_trip_event(
    player_token=agent_token,
    destination_waypoint=destination_waypoint,
    shipsymbol=ship.shipSymbol,
)
