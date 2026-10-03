"""
Shared pytest fixtures for the Koimate test suite.
Uses SQLite in-memory DB — never touches MySQL / production data.
"""
import pytest
from app import create_app
from models import db as _db


@pytest.fixture(scope="session")
def app():
    """Create application for the test session."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
        "SECRET_KEY": "test-secret",
    })

    # Re-create all tables with the in-memory DB
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """A Flask test client scoped per test function."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Provide a clean DB session; rolls back after each test."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Clean all tables between tests
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope="function")
def auth_headers(client, db_session):
    """Register a user and return JWT auth headers."""
    client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "testpass123",
    })
    res = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def seeded_products(app, db_session):
    """Insert 10 sample products for tests that need them."""
    from models import Product

    with app.app_context():
        products = [
            Product(
                name=f"Product {i}",
                category="Electronics",
                description=f"A great electronic gadget number {i}",
                price=100.0 + i,
                features_text=f"product{i} electronics gadget device",
            )
            for i in range(1, 11)
        ]
        _db.session.bulk_save_objects(products)
        _db.session.commit()

    yield

    # Cleanup is handled by db_session fixture
