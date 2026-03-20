from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

import main

client = TestClient(main.app)


def test_return_health_check():
    response: Response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}
