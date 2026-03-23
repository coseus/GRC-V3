from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "GRC Assessment Tool")
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./assessment.db")
    secret_key: str = os.getenv("SECRET_KEY", "change-me")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    default_document_classification: str = os.getenv(
        "DEFAULT_DOCUMENT_CLASSIFICATION",
        "Internal",
    )
    default_report_version: str = os.getenv("DEFAULT_REPORT_VERSION", "1.0")
    company_logo_path: str = os.getenv("COMPANY_LOGO_PATH", "")
    auto_init_db: bool = _to_bool(os.getenv("AUTO_INIT_DB", "true"), default=True)
    default_admin_username: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin").strip()
    default_admin_password: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123").strip()


settings = Settings()