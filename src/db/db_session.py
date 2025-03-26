from contextlib import contextmanager
from src.db.db import SessionLocal


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Commit if everything is successful
    except:
        session.rollback()  # Rollback in case of an error
        raise
    finally:
        session.close()
