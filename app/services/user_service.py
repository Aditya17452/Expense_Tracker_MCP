from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.hash import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.services.errors import AuthenticationError, ConflictError


def register_user(user: UserCreate, db: Session) -> User:
    if db.query(User.id).filter(User.email == user.email).first():
        raise ConflictError("A user with this email already exists")

    db_user = User(name=user.name, email=user.email, password_hash=hash_password(user.password))
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A user with this email already exists") from exc
    db.refresh(db_user)
    return db_user


def authenticate_user(email: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")
    return user


def login_user(email: str, password: str, db: Session) -> dict:
    user = authenticate_user(email, password, db)
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}
