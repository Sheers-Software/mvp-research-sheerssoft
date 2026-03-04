import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine
from app.models import Base

import pytest_asyncio

# Remove manual event_loop fixture to let pytest-asyncio handle it

@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Async HTTP client for testing the FastAPI app.
    Function scope matches the default pytest-asyncio loop scope.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """
    Ensure database tables exist before running tests.
    Silently skips if the database is unreachable — tests that fully mock
    the DB via app.dependency_overrides will still pass.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        pass  # DB unavailable; mocked tests are unaffected
    yield
