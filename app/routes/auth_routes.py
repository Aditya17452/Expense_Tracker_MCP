from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routes.errors import to_http
from app.schemas.user_schema import Token, UserCreate, UserOut
from app.services.errors import ServiceError
from app.services.user_service import login_user, register_user

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register_route(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return register_user(user, db)
    except ServiceError as exc:
        raise to_http(exc)


@router.post("/login", response_model=Token)
def login_route(email: str, password: str, db: Session = Depends(get_db)):
    try:
        return login_user(email, password, db)
    except ServiceError as exc:
        raise to_http(exc)
