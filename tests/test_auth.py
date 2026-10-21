import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from dental_clinic.core.config import settings
from dental_clinic.core.security import password_hash
from dental_clinic.models.user import User


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


def test_signup_rejects_invalid_user_data(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session

    response = client.post(
        "/auth/signup",
        json={
            "full_name": " ",
            "email": "not-an-email",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_login_returns_signed_access_token(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session
    client.post(
        "/auth/signup",
        json={
            "full_name": "Alex Patient",
            "email": "alex@example.com",
            "password": "a-long-password",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "ALEX@example.com", "password": "a-long-password"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

    claims = jwt.decode(
        response.json()["access_token"],
        settings.secret_key.get_secret_value(),
        algorithms=[settings.algorithm],
    )
    assert claims["sub"] == "1"
    assert "exp" in claims


def test_login_rejects_invalid_credentials(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session
    client.post(
        "/auth/signup",
        json={
            "full_name": "Alex Patient",
            "email": "alex@example.com",
            "password": "a-long-password",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "alex@example.com", "password": "incorrect-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_rejects_inactive_user(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, test_session = client_and_session
    client.post(
        "/auth/signup",
        json={
            "full_name": "Alex Patient",
            "email": "alex@example.com",
            "password": "a-long-password",
        },
    )
    with test_session() as db:
        user = db.scalar(select(User).where(User.email == "alex@example.com"))
        assert user is not None
        user.is_active = False
        db.commit()

    response = client.post(
        "/auth/login",
        json={"email": "alex@example.com", "password": "a-long-password"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"
