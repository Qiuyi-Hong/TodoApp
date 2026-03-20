from fastapi import status
from httpx import Response

from models import Users
from routers.users import get_current_authenticated_user, get_db

from .utils import app, client, override_get_current_user, override_get_db, test_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_authenticated_user] = override_get_current_user


def test_return_user(test_user: Users):
    response: Response = client.get("/get_current_user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"
    assert response.json()["username"] == "testuser"
