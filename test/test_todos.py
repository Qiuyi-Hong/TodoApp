from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm.session import Session

# from routers.auth import get_current_user, get_db
from main import app
from models import Todos
from routers.todos import get_current_user, get_db

from .utils import override_get_current_user, override_get_db, test_todo, TestingSessionLocal # type: ignore  # noqa: F401

# # PostgreSQL connection:
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Test1234@localhost:5432/testDB"

# engine: Engine = create_engine(SQLALCHEMY_DATABASE_URL)
# TestingSessionLocal: sessionmaker[Session] = sessionmaker(
#     autocommit=False, autoflush=False, bind=engine
# )

# Base.metadata.create_all(bind=engine)


# def override_get_db():
#     db: Session = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def override_get_current_user() -> dict[str, str | int]:
#     return {"username": "testuser", "user_role": "admin", "id": 1}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


# @pytest.fixture
# def test_todo():
#     db: Session = TestingSessionLocal()
#     with engine.connect() as connection:
#         connection.execute(text("DELETE FROM todos"))
#         connection.execute(text("DELETE FROM users"))
#         connection.commit()

#     user = Users(
#         id=1,
#         email="test@example.com",
#         username="testuser",
#         first_name="Test",
#         last_name="User",
#         hashed_password="not-relevant-for-this-test",
#         is_active=True,
#         role="admin",
#         phone_number="123-456-7890",
#     )
#     todo = Todos(
#         title="Test Todo",
#         description="This is a test todo",
#         priority=3,
#         complete=False,
#         owner_id=1,
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     db.add(todo)
#     db.commit()
#     db.refresh(todo)
#     try:
#         yield todo
#     finally:
#         db.close()
#         with engine.connect() as connection:
#             connection.execute(text("DELETE FROM todos"))
#             connection.execute(text("DELETE FROM users"))
#             connection.commit()


def test_read_all_authenticated(test_todo: Todos):
    response: Response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "complete": False,
            "title": "Test Todo",
            "description": "This is a test todo",
            "id": test_todo.id,
            "priority": 3,
            "owner_id": 1,
        }
    ]


def test_read_one_authenticated(test_todo: Todos):
    response: Response = client.get(f"/todos/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "complete": False,
        "title": "Test Todo",
        "description": "This is a test todo",
        "id": test_todo.id,
        "priority": 3,
        "owner_id": 1,
    }


def test_create_todo_authenticated_not_found():
    response: Response = client.get("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_create_todo(test_todo: Todos):
    request_date: dict[str, str | int | bool] = {
        "title": "New Todo",
        "description": "This is a new todo",
        "priority": 2,
        "complete": False,
    }

    response: Response = client.post("/todos/todo", json=request_date)
    assert response.status_code == status.HTTP_201_CREATED
    
    db: Session = TestingSessionLocal()
    model: Todos | None = db.query(Todos).filter(Todos.title == request_date["title"]).first()
    assert model is not None
    assert model.description == request_date["description"]
    assert model.priority == request_date["priority"]
    assert model.complete == request_date["complete"]
    
def test_update_todo(test_todo: Todos):
    request_date: dict[str, str | int | bool] = {
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 4,
        "complete": True,
    }

    response: Response = client.put(f"/todos/todo/{test_todo.id}", json=request_date)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db: Session = TestingSessionLocal()
    model: Todos | None = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert model is not None
    assert model.title == request_date["title"]
    assert model.description == request_date["description"]
    assert model.priority == request_date["priority"]
    assert model.complete == request_date["complete"]
    
def test_update_todo_not_found(test_todo: Todos):
    request_date: dict[str, str | int | bool] = {
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 4,
        "complete": True,
    }

    response: Response = client.put("/todos/todo/999", json=request_date)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
    
def test_delete_todo(test_todo: Todos):
    response: Response = client.delete(f"/todos/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db: Session = TestingSessionLocal()
    model: Todos | None = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert model is None
    
def test_delete_todo_not_found(test_todo: Todos):
    response: Response = client.delete("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
