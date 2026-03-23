from __future__ import annotations

import json
from pathlib import Path

from app.frameworks.registry import FRAMEWORK_REGISTRY
from app.schemas.framework import FrameworkSchema

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_framework_options():
    return dict(sorted(FRAMEWORK_REGISTRY.items(), key=lambda item: item[1]["name"]))


def load_framework_data(framework_code: str):
    if framework_code not in FRAMEWORK_REGISTRY:
        raise ValueError(f"Unknown framework: {framework_code}")

    framework_file = FRAMEWORK_REGISTRY[framework_code]["file"]
    path = PROJECT_ROOT / framework_file

    if not path.exists():
        raise FileNotFoundError(f"Framework file not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))

    try:
        validated = FrameworkSchema.model_validate(raw)
    except Exception as exc:
        raise ValueError(f"Invalid framework format for '{framework_code}': {exc}") from exc

    return validated.model_dump()