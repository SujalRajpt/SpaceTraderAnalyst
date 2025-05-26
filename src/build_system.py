from src.objects.player import Player
from src.objects.market import Market
from src.db.db_session import get_session
from src.db.models import Agent

with get_session() as session:
    agent = session.query(Agent).filter_by(id=1).first()

    if agent:
        agent_token = agent.agent_token
    else:
        agent_token = None


player = Player(agent_token=agent_token)
market = Market(player)
market.build_database()
