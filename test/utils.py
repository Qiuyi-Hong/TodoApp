import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

# from routers.auth import get_current_user, get_db
from models import Base, Todos, Users
from routers.auth import bcrypt_context
from main import app
from fastapi.testclient import TestClient

# PostgreSQL connection:
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Test1234@localhost:5432/testDB"

engine: Engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db: Session = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user() -> dict[str, str | int]:
    return {"username": "testuser", "role": "admin", "id": 1}


# app.dependency_overrides[get_db] = override_get_db
# app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    db: Session = TestingSessionLocal()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.execute(text("DELETE FROM users"))
        connection.commit()

    user = Users(
        id=1,
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("testpassword"),
        is_active=True,
        role="admin",
        phone_number="123-456-7890",
    )
    todo = Todos(
        title="Test Todo",
        description="This is a test todo",
        priority=3,
        complete=False,
        owner_id=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(todo)
    db.commit()
    db.refresh(todo)
    try:
        yield todo
    finally:
        db.close()
        with engine.connect() as connection:
            connection.execute(text("DELETE FROM todos"))
            connection.execute(text("DELETE FROM users"))
            connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("testpassword"),
        is_active=True,
        role="admin",
        phone_number="123-456-7890",
    )
    db: Session = TestingSessionLocal()
    db.add(user)
    db.commit()
    # db.refresh(user)

    yield user

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()
