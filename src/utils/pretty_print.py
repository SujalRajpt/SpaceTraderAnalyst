import json


def pretty_print(data):
    """Formats and prints JSON data in a readable way."""
    print(json.dumps(data, indent=4))
