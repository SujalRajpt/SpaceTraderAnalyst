from src.objects.player import Player, PlayerCreator
from src.objects.ship import Ship
from src.utils.config import a1
import json


def pretty_print(data):
    """Formats and prints JSON data in a readable way."""
    print(json.dumps(data, indent=4))


# # Create a new player
# player_data = PlayerCreator.create_player("TRADER_002")
# if player_data:
#     agent_token = player_data.get("data", {}).get("token")
#     print(agent_token)
#     if agent_token:
#         my_player = Player(agent_token)
#         print(my_player.view_agent())  # Fetch agent details


my_player = Player(a1)
print(my_player.current_system)
ships = my_player.view_my_ships()
ship_symbols = [ship["symbol"] for ship in ships["data"]]
# pretty_print(ships)

ship = Ship(my_player, ship_symbols[0])

pretty_print(ship.get_in_orbit())
