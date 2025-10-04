# Shared test configuration and fixtures for user-service

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from unittest.mock import AsyncMock, patch

# Import your app and dependencies
from app.main import app
from app.core.database import get_db, Base
from app.core.config import get_settings
from app.models.user import User
from app.models.business_unit import BusinessUnit
from app.schemas.user import UserCreate
from app.core.security import create_access_token, get_password_hash

# Test database URL - using SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client(test_session):
    """Create test client with database override."""
    def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Test user data fixture."""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "user",
        "is_active": True,
        "tenant_id": "test-tenant-123"
    }

@pytest_asyncio.fixture
async def test_user(test_session, test_user_data):
    """Create a test user in the database."""
    password_hash = get_password_hash("testpassword123")
    
    user = User(
        email=test_user_data["email"],
        full_name=test_user_data["full_name"],
        hashed_password=password_hash,
        role=test_user_data["role"],
        is_active=test_user_data["is_active"],
        tenant_id=test_user_data["tenant_id"]
    )
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    return user

@pytest.fixture
def test_admin_user_data():
    """Test admin user data fixture."""
    return {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "tenant_id": "test-tenant-123"
    }

@pytest_asyncio.fixture
async def test_admin_user(test_session, test_admin_user_data):
    """Create a test admin user in the database."""
    password_hash = get_password_hash("adminpassword123")
    
    user = User(
        email=test_admin_user_data["email"],
        full_name=test_admin_user_data["full_name"],
        hashed_password=password_hash,
        role=test_admin_user_data["role"],
        is_active=test_admin_user_data["is_active"],
        tenant_id=test_admin_user_data["tenant_id"]
    )
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    return user

@pytest.fixture
def test_business_unit_data():
    """Test business unit data fixture."""
    return {
        "name": "Test Business Unit",
        "description": "A test business unit",
        "tenant_id": "test-tenant-123"
    }

@pytest_asyncio.fixture
async def test_business_unit(test_session, test_business_unit_data):
    """Create a test business unit in the database."""
    business_unit = BusinessUnit(
        name=test_business_unit_data["name"],
        description=test_business_unit_data["description"],
        tenant_id=test_business_unit_data["tenant_id"]
    )
    
    test_session.add(business_unit)
    await test_session.commit()
    await test_session.refresh(business_unit)
    
    return business_unit

@pytest.fixture
def user_token(test_user):
    """Create JWT token for test user."""
    return create_access_token(
        data={
            "sub": test_user.email,
            "user_id": str(test_user.id),
            "tenant_id": test_user.tenant_id,
            "role": test_user.role
        }
    )

@pytest.fixture
def admin_token(test_admin_user):
    """Create JWT token for test admin user."""
    return create_access_token(
        data={
            "sub": test_admin_user.email,
            "user_id": str(test_admin_user.id),
            "tenant_id": test_admin_user.tenant_id,
            "role": test_admin_user.role
        }
    )

@pytest.fixture
def auth_headers(user_token):
    """Create authorization headers with user token."""
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def admin_auth_headers(admin_token):
    """Create authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer for testing."""
    with patch('app.core.messaging.kafka_producer') as mock:
        mock_producer = AsyncMock()
        mock.return_value = mock_producer
        yield mock_producer

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch('app.core.cache.redis_client') as mock:
        mock_redis = AsyncMock()
        mock.return_value = mock_redis
        yield mock_redis

@pytest.fixture
def mock_email_service():
    """Mock email service for testing."""
    with patch('app.services.notification_service.send_email') as mock:
        mock_email = AsyncMock()
        mock.return_value = {"status": "sent", "message_id": "test-123"}
        yield mock_email

@pytest.fixture(autouse=True)
def override_settings():
    """Override settings for testing."""
    test_settings = get_settings()
    test_settings.DATABASE_URL = TEST_DATABASE_URL
    test_settings.TESTING = True
    test_settings.SECRET_KEY = "test-secret-key"
    test_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    test_settings.REDIS_URL = "redis://localhost:6379/1"  # Use test Redis DB
    test_settings.KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
    test_settings.LOG_LEVEL = "DEBUG"
    
    return test_settings

# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "contract: mark test as a contract test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add unit marker to tests in unit/ directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in integration/ directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # Add contract marker to tests in contract/ directory
        elif "contract" in str(item.fspath):
            item.add_marker(pytest.mark.contract)

# Test utilities
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_user_data(**kwargs):
        """Create user test data with optional overrides."""
        default_data = {
            "email": "user@example.com",
            "full_name": "Test User",
            "password": "testpassword123",
            "role": "user",
            "is_active": True,
            "tenant_id": "test-tenant-123"
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_business_unit_data(**kwargs):
        """Create business unit test data with optional overrides."""
        default_data = {
            "name": "Test Business Unit",
            "description": "A test business unit",
            "tenant_id": "test-tenant-123"
        }
        default_data.update(kwargs)
        return default_data

@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory
