from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt import InvalidTokenError, decode_access_token
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user