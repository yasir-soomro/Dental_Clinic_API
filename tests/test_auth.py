from collections.abc import Generator

import pytest
import uvicorn
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from dental_clinic.core.security import password_hash
from dental_clinic.db.database import Base, get_db
from dental_clinic.main import app
from dental_clinic.models.user import User


def test_cli_starts_api(monkeypatch: pytest.MonkeyPatch) -> None:
    from dental_clinic.cli import main

    run_options: dict[str, object] = {}

    def fake_run(app: str, host: str, port: int) -> None:
        run_options.update(app=app, host=host, port=port)

    monkeypatch.setattr(uvicorn, "run", fake_run)

    main()

    assert run_options == {
        "app": "dental_clinic.main:app",
        "host": "127.0.0.1",
        "port": 8000,
    }


@pytest.fixture
def client_and_session(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[
    tuple[TestClient, sessionmaker[Session]], None, None
]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr("dental_clinic.main.engine", engine)
    test_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db() -> Generator[Session, None, None]:
        with test_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client, test_session
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


def test_signup_persists_hashed_user_and_rejects_duplicate_email(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, test_session = client_and_session
    payload = {
        "full_name": "  Alex Patient  ",
        "email": "alex@example.com",
        "password": "a-long-password",
    }

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "full_name": "Alex Patient",
        "email": "alex@example.com",
        "role": "patient",
        "is_active": True,
    }
    assert "hashed_password" not in response.json()

    with test_session() as db:
        user = db.scalar(select(User).where(User.email == "alex@example.com"))
        assert user is not None
        assert user.full_name == "Alex Patient"
        assert user.hashed_password != payload["password"]
        assert password_hash.verify(payload["password"], user.hashed_password)

    duplicate_response = client.post(
        "/auth/signup",
        json={**payload, "email": "alex@EXAMPLE.com"},
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "Email already registered"


def test_health_endpoint(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
