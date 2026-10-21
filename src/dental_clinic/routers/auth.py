
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dental_clinic.core.security import hash_password
from dental_clinic.db.database import get_db
from dental_clinic.models.user import User
from dental_clinic.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    email = str(user_data.email).lower()

    # Check whether the email is already registered.
    existing_user = db.scalar(select(User).where(User.email == email))

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create a new user. Never store the plain password.
    new_user = User(
        full_name=user_data.full_name,
        email=email,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError as exc:
        db.rollback()
        if db.scalar(select(User.id).where(User.email == email)) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            ) from exc
        raise

    return new_user