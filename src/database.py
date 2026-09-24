from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"  # SQLite database URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} #"check_same_thread": False . this is SQLLite especific
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # A factory for creating new Session objects, which are used to interact with the database. The session is configured to not autocommit changes and not autoflush changes to the database until explicitly requested. The session is bound to the engine created earlier, which connects to the SQLite database specified by SQLALCHEMY_DATABASE_URL.
# Standard FastAPI Pattern.

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db