from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_URL


def ensure_database():
    """For PostgreSQL, create the target database if it does not exist yet."""
    url = make_url(DATABASE_URL)
    if not url.drivername.startswith("postgresql"):
        return
    try:
        with create_engine(url).connect():
            return
    except Exception:
        pass

    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
            ).scalar()
            if exists is None:
                conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    finally:
        admin_engine.dispose()


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    ensure_database()
    from app.models import expense, user  # noqa: F401  (register models)

    Base.metadata.create_all(bind=engine)
