from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Session:  # type: ignore[misc]
    db = SessionLocal()
    try:
        yield db  # type: ignore[misc]
    finally:
        db.close()
