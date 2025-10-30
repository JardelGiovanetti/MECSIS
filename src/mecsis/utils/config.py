from __future__ import annotations

import os
import sys
from pathlib import Path


def _runtime_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[3]


def _resource_base_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


RUNTIME_BASE_DIR = _runtime_base_dir()
RESOURCE_BASE_DIR = _resource_base_dir()


def ensure_data_dir() -> Path:
    data_dir = RUNTIME_BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path() -> Path:
    env_path = os.getenv("MECSIS_DB_PATH")
    if env_path:
        db_path = Path(env_path)
    else:
        db_path = ensure_data_dir() / "mecsis.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def resource_path(*relative_parts: str) -> Path:
    return RESOURCE_BASE_DIR.joinpath(*relative_parts)
