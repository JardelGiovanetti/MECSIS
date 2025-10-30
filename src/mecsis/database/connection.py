from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import sqlite3

from ..utils.config import get_database_path, resource_path


class DatabaseManager:
    def __init__(self) -> None:
        self.db_path = get_database_path()
        self._initialized = False

    def _load_schema(self) -> str:
        schema_path = resource_path("mecsis", "database", "schema.sql")
        if not schema_path.exists():
            schema_path = Path(__file__).resolve().with_name("schema.sql")
        return schema_path.read_text(encoding="utf-8")

    def _apply_schema(self) -> None:
        script = self._load_schema()
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("PRAGMA foreign_keys = ON;")
            conn.executescript(script)
        self._initialized = True

    def initialize(self) -> None:
        if self._initialized:
            return
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._apply_schema()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        self.initialize()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


database_manager = DatabaseManager()
