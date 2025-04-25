"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.database import get_session
from src.main import app
from src.models import Category, User


@pytest.fixture(name="session")
def session_fixture():
    """
    Create a test database session.
    
    Yields:
        Session: SQLModel session
    """
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create a test client with a test database session.
    
    Args:
        session: Test database session
        
    Returns:
        TestClient: FastAPI test client
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """
    Create a test user.
    
    Args:
        session: Test database session
        
    Returns:
        User: Test user
    """
    from src.services.auth import get_password_hash
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        first_name="Test",
        last_name="User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_categories")
def test_categories_fixture(session: Session, test_user: User):
    """
    Create test categories.
    
    Args:
        session: Test database session
        test_user: Test user
        
    Returns:
        list[Category]: Test categories
    """
    categories = [
        Category(name="Food", user_id=test_user.id),
        Category(name="Transportation", user_id=test_user.id),
        Category(name="Entertainment", user_id=test_user.id),
    ]
    for category in categories:
        session.add(category)
    session.commit()
    
    for category in categories:
        session.refresh(category)
    
    return categories
