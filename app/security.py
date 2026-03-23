from __future__ import annotations

import bcrypt


def _validate_bcrypt_password_length(password: str) -> None:
    if password is None:
        raise ValueError("Parola lipseste.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Parola este prea lunga pentru bcrypt. Foloseste maxim 72 bytes.")


def hash_password(password: str) -> str:
    _validate_bcrypt_password_length(password)
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    _validate_bcrypt_password_length(password)

    if not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except Exception:
        return False


def validate_password_strength(password: str) -> None:
    password = (password or "").strip()

    if len(password) < 8:
        raise ValueError("Parola trebuie sa aiba minim 8 caractere.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Parola trebuie sa aiba maxim 72 bytes pentru bcrypt.")

    if password.lower() in {"password", "admin123", "12345678", "qwerty123"}:
        raise ValueError("Parola este prea slaba.")