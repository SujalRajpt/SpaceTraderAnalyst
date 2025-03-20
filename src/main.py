import json
from src.objects.player import Player
from src.objects.ship import Ship
from src.utils.config import a2


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


# my_player = Player(a1)
# ships = my_player.view_my_ships()
# ship_symbols = [ship["symbol"] for ship in ships["data"]]
# # pretty_print(ships)

# ship = Ship(my_player, ship_symbols[0])
# print(my_player.current_system, my_player.current_waypoint)
# pretty_print(my_player.view_contracts())


player = Player(a2)

ship_symbols = [x["symbol"] for x in player.view_my_ships().get("data", [])]
# print(ship_symbols)
# pretty_print(player.fetch_agent_info())

response = player.view_my_ships()  # Assuming this returns a dictionary


# Extract ship details by symbol
def get_ship_details(response, ship_symbol):
    for ship in response["data"]:
        if ship["symbol"] == ship_symbol:
            return ship  # Return the ship details

    return None  # If ship not found


# Example usage
ship_symbol = "TEST_USER-1"  # Change this to the ship you want
ship_details = get_ship_details(response, ship_symbol)

# Pretty print ship details
if ship_details:
    print(json.dumps(ship_details, indent=4))
else:
    print(f"Ship '{ship_symbol}' not found.")
