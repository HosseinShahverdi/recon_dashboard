import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.session import Base
from app.db.models import Domain, Scan, Asset, Observation


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create an in-memory SQLite database for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest_asyncio.fixture
async def sample_domain(test_db):
    """Create a test domain."""
    domain = Domain(name="example.com")
    test_db.add(domain)
    await test_db.commit()
    await test_db.refresh(domain)
    return domain


@pytest_asyncio.fixture
async def sample_scan(test_db, sample_domain):
    """Create a test scan."""
    scan = Scan(domain_id=sample_domain.id, status="completed", mode="quick")
    test_db.add(scan)
    await test_db.commit()
    await test_db.refresh(scan)
    return scan