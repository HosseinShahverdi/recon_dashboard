import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_db


@pytest_asyncio.fixture
async def client(test_db):
    """Create an async test client."""
    transport = ASGITransport(app=app)
    previous_override = app.dependency_overrides.get(get_db)

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """GET / should return 200."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_create_domain(client):
    """POST /api/v1/domains/ should create a new domain."""
    response = await client.post("/api/v1/domains/", json={"name": "test.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_duplicate_domain_rejected(client):
    """Creating the same domain twice should fail."""
    await client.post("/api/v1/domains/", json={"name": "duplicate.com"})
    response = await client.post("/api/v1/domains/", json={"name": "duplicate.com"})
    assert response.status_code == 400