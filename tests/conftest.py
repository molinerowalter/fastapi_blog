import asyncio
import os
import sys
from collections.abc import AsyncGenerator

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://walter:Caiman_45@localhost:5432/test_blog"
)
os.environ["S3_BUCKET_NAME"] = "test-bucket"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

os.environ["S3_ACCESS_KEY_ID"] = "testing"
os.environ["S3_SECRET_ACCESS_KEY"] = "testing"
os.environ["S3_REGION"] = "us-east-2"

#Boto3 uses these environment variables for AWS credentials and region configuration, so we set them here for testing purposes.
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-2"

import boto3
import pytest
from httpx import ASGITransport, AsyncClient
from moto import mock_aws
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database import Base, get_db
from main import app

pytest_plugins = ["anyio"] # Permite crear funciones de prueba asíncronas con pytest y anyio.

@pytest.fixture(scope="session") #convierte la función en un fixture de pytest que se ejecuta una vez por sesión de prueba.
def anyio_backend():
    if sys.platform == "win32":
        return "asyncio", {"loop_factory": asyncio.SelectorEventLoop}
    return "asyncio"  # Configura AnyIO para usar el backend asyncio.

#Crea el motor de nuestra base de datos de prueba usando SQLAlchemy y la URL de la base de datos proporcionada en las variables de entorno. Se utiliza NullPool para evitar el uso de un pool de conexiones, lo que es útil en pruebas para evitar problemas de concurrencia.
@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
    )
    return engine

@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()

@pytest.fixture # Si no hay ambito se ejecuta para cada función de prueba.
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()

@pytest.fixture 
def mocked_aws(): #No es asincrona, ya que la creación del cliente S3 y la creación del bucket se realiza de manera sincrónica.
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-2")
        s3.create_bucket(
            Bucket=os.environ["S3_BUCKET_NAME"],
            CreateBucketConfiguration={"LocationConstraint": "us-east-2"},
        )
        yield s3

@pytest.fixture
async def client(
    db_session: AsyncSession,
    mocked_aws,
) -> AsyncGenerator[AsyncClient]:

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> dict:
    response = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> str:
    response = await client.post(
        "/api/users/token",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}



