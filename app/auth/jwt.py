from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
from typing import Any

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SECRET as SECRET_KEY

ALGORITHM = "HS256"


class InvalidTokenError(ValueError):
    pass


def _encode_part(value: object) -> str:
    encoded = json.dumps(value, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(encoded).rstrip(b"=").decode()


def _decode_part(value: str) -> dict[str, Any]:
    padding = "=" * (-len(value) % 4)
    decoded = json.loads(base64.urlsafe_b64decode(value + padding))
    if not isinstance(decoded, dict):
        raise InvalidTokenError("Invalid token")
    return decoded


def create_access_token(id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    header = _encode_part({"alg": ALGORITHM, "typ": "JWT"})
    payload = _encode_part({"sub": str(id), "exp": expire.timestamp()})
    message = f"{header}.{payload}".encode()
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return f"{header}.{payload}.{encoded_signature}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        header, payload, signature = token.split(".")
        message = f"{header}.{payload}".encode()
        expected = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
        actual = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
        decoded_payload = _decode_part(payload)
        if not hmac.compare_digest(actual, expected):
            raise InvalidTokenError("Invalid signature")
        exp_value = decoded_payload.get("exp")
        if not isinstance(exp_value, (int, float)):
            raise InvalidTokenError("Invalid token")
        if float(exp_value) <= datetime.now(timezone.utc).timestamp():
            raise InvalidTokenError("Expired token")
        return decoded_payload
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise InvalidTokenError("Invalid token") from exc