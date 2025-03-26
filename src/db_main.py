from src.db.db import init_db, SessionLocal


init_db()
session = SessionLocal()
session.commit()
session.close()
