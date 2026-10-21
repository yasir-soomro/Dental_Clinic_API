from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dental_clinic.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from dental_clinic.models.user import User
from dental_clinic.schemas.auth import LoginRequest
from dental_clinic.schemas.user import UserCreate


def register_user(user_data: UserCreate, db: Session) -> User:
    email = str(user_data.email).lower()
    existing_user = db.scalar(select(User).where(User.email == email))

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        full_name=user_data.full_name,
        email=email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        if db.scalar(select(User.id).where(User.email == email)) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            ) from exc
        raise

    return user


def authenticate_user(credentials: LoginRequest, db: Session) -> str:
    email = str(credentials.email).lower()
    user = db.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(
        credentials.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return create_access_token(user.id)
