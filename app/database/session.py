from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
The code below is for testing only.
"""
def create_db_engine():
    return create_engine(settings.DATABASE_URL)

engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    engine = create_db_engine()
    SessionLocal = sessionmaker(bind=engine)

