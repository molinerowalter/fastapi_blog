from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"  # SQLite database URL

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} #"check_same_thread": False . this is SQLLite especific
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
) # A factory for creating new Session objects, which are used to interact with the database. The session is configured to not autocommit changes and not autoflush changes to the database until explicitly requested. The session is bound to the engine created earlier, which connects to the SQLite database specified by SQLALCHEMY_DATABASE_URL.
# Standard FastAPI Pattern.

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session