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


player = Player.create_player("sujal")
