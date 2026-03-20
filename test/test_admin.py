from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session

from main import app
from models import Todos
from routers.admin import get_current_user, get_db

from .utils import ( 
    TestingSessionLocal,
    override_get_current_user,
    override_get_db,
    test_todo, # type: ignore  # noqa: F401
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


client = TestClient(app)


def test_admin_read_all_authenticated(test_todo: Todos):  # noqa: F811
    response: Response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": test_todo.id,
            "title": test_todo.title,
            "description": test_todo.description,
            "priority": test_todo.priority,
            "complete": test_todo.complete,
            "owner_id": test_todo.owner_id,
        }
    ]


def test_admin_delete_todo(test_todo: Todos):  # noqa: F811
    response: Response = client.delete(f"/admin/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db: Session = TestingSessionLocal()
    model: Todos | None = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert model is None

def test_admin_delete_todo_not_found():
    response: Response = client.delete("/admin/todo/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}