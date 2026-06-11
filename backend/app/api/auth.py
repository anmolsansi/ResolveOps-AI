from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.models import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RoleUpdateRequest,
    TokenResponse,
    UserListResponse,
    UserResponse,
)
from app.services.audit import record_audit

router = APIRouter()

VALID_ROLES = {"admin", "member", "viewer"}


@router.post("/register", response_model=TokenResponse)
def register(
    payload: RegisterRequest, request: Request, db: Session = Depends(get_db)
) -> TokenResponse:
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=422, detail="A valid email is required")
    if len(payload.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    # The first registered user becomes an admin; everyone else defaults to member.
    is_first = db.query(User).count() == 0
    requested = (payload.role or "").lower()
    if is_first:
        role = "admin"
    elif requested in VALID_ROLES:
        role = requested
    else:
        role = "member"

    user = User(email=email, password_hash=hash_password(payload.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)

    record_audit(
        db,
        actor_email=email,
        action="user.register",
        resource_type="user",
        resource_id=str(user.id),
        detail=f"role={role}",
        ip_address=request.client.host if request.client else None,
    )
    token = create_access_token(str(user.id), user.email, user.role)
    return TokenResponse(access_token=token, role=user.role, email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    record_audit(
        db,
        actor_email=email,
        action="user.login",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    token = create_access_token(str(user.id), user.email, user.role)
    return TokenResponse(access_token=token, role=user.role, email=user.email)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.get("/users", response_model=UserListResponse)
def list_users(
    _: User = Depends(require_admin), db: Session = Depends(get_db)
) -> UserListResponse:
    users = db.query(User).order_by(User.created_at.asc()).all()
    return UserListResponse(
        users=[
            UserResponse(
                id=u.id,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at,
            )
            for u in users
        ]
    )


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    payload: RoleUpdateRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserResponse:
    role = payload.role.lower()
    if role not in VALID_ROLES:
        raise HTTPException(status_code=422, detail=f"role must be one of {sorted(VALID_ROLES)}")
    target = db.get(User, _parse_uuid(user_id))
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    target.role = role
    db.commit()
    db.refresh(target)
    record_audit(
        db,
        actor_email=admin.email,
        action="user.role_change",
        resource_type="user",
        resource_id=str(target.id),
        detail=f"role={role}",
    )
    return UserResponse(
        id=target.id,
        email=target.email,
        role=target.role,
        is_active=target.is_active,
        created_at=target.created_at,
    )


def _parse_uuid(value: str):
    import uuid

    try:
        return uuid.UUID(value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid id")
