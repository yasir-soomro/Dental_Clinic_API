from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker


def test_health_endpoint(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
