import unittest
from src.objects.player import Player
from src.objects.ship import SpaceShip
from src.db.db_session import get_session
from src.db.models import Agent


class TestShipDBMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup data once before all tests run
        with get_session() as session:
            agent = session.query(Agent).filter_by(id=3).first()
            if not agent:
                raise ValueError("Agent with id=3 not found for tests.")
            cls.agent_token = agent.agent_token
            cls.symbol = agent.symbol

        cls.player = Player(cls.symbol)
        cls.ship = SpaceShip.load_or_create(
            shipSymbol=cls.player.shipSymbols[0], player=cls.player
        )
        cls.ship2 = SpaceShip.load_or_create(
            shipSymbol=cls.player.shipSymbols[1], player=cls.player
        )

    def test_fetch_modules_from_db(self):
        modules = self.ship.db.fetch_modules_from_db()
        self.assertIsInstance(modules, list)
        for module in modules:
            self.assertIsInstance(module, dict)
            self.assertIn("id", module)
            self.assertIn("name", module)

    def test_fetch_mounts_from_db(self):
        mounts = self.ship.db.fetch_mounts_from_db()
        self.assertIsInstance(mounts, list)
        for mount in mounts:
            self.assertIsInstance(mount, dict)
            self.assertIn("id", mount)
            self.assertIn("name", mount)

    def test_fetch_navigation_info_from_db(self):
        nav = self.ship.db.fetch_navigation_info_from_db()
        if nav is not None:
            self.assertIsInstance(nav, dict)
            self.assertIn("origin_waypoint", nav)
            self.assertIn("status", nav)
        else:
            self.assertIsNone(nav)

    def test_fetch_shipfuel_from_db(self):
        fuel = self.ship.db.fetch_shipfuel_from_db()
        if fuel is not None:
            self.assertIsInstance(fuel, dict)
            self.assertIn("current", fuel)
            self.assertIn("capacity", fuel)
        else:
            self.assertIsNone(fuel)

    def test_fetch_shipcargo_from_db(self):
        cargo = self.ship.db.fetch_shipcargo_from_db()
        if cargo is not None:
            self.assertIsInstance(cargo, dict)
            self.assertIn("current", cargo)
            self.assertIn("inventory", cargo)
        else:
            self.assertIsNone(cargo)

    def test_fetch_shipcrew_from_db(self):
        crew = self.ship.db.fetch_shipcrew_from_db()
        if crew is not None:
            self.assertIsInstance(crew, dict)
            self.assertIn("current", crew)
            self.assertIn("morale", crew)
        else:
            self.assertIsNone(crew)

    def test_fetch_shipframe_from_db(self):
        frame = self.ship.db.fetch_shipframe_from_db()
        if frame is not None:
            self.assertIsInstance(frame, dict)
            self.assertIn("symbol", frame)
            self.assertIn("condition", frame)
        else:
            self.assertIsNone(frame)

    def test_fetch_shipreactor_from_db(self):
        reactor = self.ship.db.fetch_shipreactor_from_db()
        if reactor is not None:
            self.assertIsInstance(reactor, dict)
            self.assertIn("symbol", reactor)
            self.assertIn("power_output", reactor)
        else:
            self.assertIsNone(reactor)

    def test_fetch_shipengine_from_db(self):
        engine = self.ship.db.fetch_shipengine_from_db()
        if engine is not None:
            self.assertIsInstance(engine, dict)
            self.assertIn("symbol", engine)
            self.assertIn("speed", engine)
        else:
            self.assertIsNone(engine)

    def test_fetch_shipcooldown_from_db(self):
        cooldown = self.ship.db.fetch_shipcooldown_from_db()
        if cooldown is not None:
            self.assertIsInstance(cooldown, dict)
            self.assertIn("total_seconds", cooldown)
            self.assertIn("remaining_seconds", cooldown)
        else:
            self.assertIsNone(cooldown)
