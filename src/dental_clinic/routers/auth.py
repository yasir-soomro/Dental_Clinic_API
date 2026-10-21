from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from dental_clinic.db.session import get_db
from dental_clinic.schemas.auth import LoginRequest, TokenResponse
from dental_clinic.schemas.user import UserCreate, UserResponse
from dental_clinic.services.auth import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    return register_user(user_data, db)


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    access_token = authenticate_user(credentials, db)
    return TokenResponse(access_token=access_token)
