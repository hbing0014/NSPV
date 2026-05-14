from fastapi import APIRouter, Depends, Header, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.tables import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut


router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized()

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if payload is None:
        raise unauthorized()

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.isdigit():
        raise unauthorized()

    user = db.get(User, int(subject))
    if user is None:
        raise unauthorized()
    return user


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = normalize_email(request.email)
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise ApiError(
            code="EMAIL_ALREADY_REGISTERED",
            message="Email is already registered.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"email": email},
        )

    user = User(
        email=email,
        name=request.name,
        password_hash=hash_password(request.password),
        plan_type="free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == normalize_email(request.email)))
    if user is None or not verify_password(request.password, user.password_hash):
        raise ApiError(
            code="INVALID_CREDENTIALS",
            message="Invalid email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return auth_response(user)


@router.get("/profile", response_model=UserOut)
def profile(current_user: User = Depends(get_current_user)) -> UserOut:
    return user_to_response(current_user)


def auth_response(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(str(user.id)), user=user_to_response(user))


def user_to_response(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email or "",
        name=user.name,
        plan_type=user.plan_type,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def normalize_email(email: str) -> str:
    return email.strip().lower()


def unauthorized() -> ApiError:
    return ApiError(
        code="UNAUTHORIZED",
        message="Authentication credentials are invalid or missing.",
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
