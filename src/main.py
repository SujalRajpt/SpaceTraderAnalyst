import json
from src.objects.player import Player
from src.objects.ship import Ship
from src.db.db_session import get_session
from src.db.models import Agent, Ship


def pretty_print(data):
    """Formats and prints JSON data in a readable way."""
    print(json.dumps(data, indent=4))


player = Player.create_player("sujal")

# with get_session() as session:
#     agent = session.query(Agent).filter_by(id=3).first()

#     if agent:
#         agent_token = agent.agent_token
#     else:
#         agent_token = None

# if agent_token:
#     player = Player(agent_token)
#     print(player.current_system)
#     print(player.shipSymbol)
# else:
#     print("Agent with ID 7 not found.")
