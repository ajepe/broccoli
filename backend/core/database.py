from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import get_settings

settings = get_settings()

# Use SQLite for local development (default), PostgreSQL for production
if settings.USE_SQLITE:
    DATABASE_URL = "sqlite:///./odoo_cloud.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = (
        f"postgresql://{settings.EXTERNAL_DB_USER}:{settings.EXTERNAL_DB_PASSWORD}"
        f"@{settings.EXTERNAL_DB_HOST}:{settings.EXTERNAL_DB_PORT}/{settings.EXTERNAL_DB_NAME}"
    )
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
