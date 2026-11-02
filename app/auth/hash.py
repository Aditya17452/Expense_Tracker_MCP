import hashlib
import hmac
import secrets


_ALGORITHM = "sha256"
_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        _ALGORITHM, password.encode(), salt, _ITERATIONS
    )
    return f"pbkdf2_{_ALGORITHM}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        scheme, iterations, salt_hex, digest_hex = hashed_password.split("$")
        if scheme != f"pbkdf2_{_ALGORITHM}":
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            _ALGORITHM,
            password.encode(),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(actual, expected)
