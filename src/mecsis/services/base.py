from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Set

import sqlite3

from ..database.connection import database_manager


class BaseService:
    table_name: str
    primary_key: str = "id"
    def __init__(self) -> None:
        self._columns_cache: Optional[Set[str]] = None

    def _fetch_columns(self) -> Set[str]:
        if self._columns_cache is None:
            with database_manager.get_connection() as conn:
                cursor = conn.execute(f"PRAGMA table_info({self.table_name})")
                self._columns_cache = {row["name"] for row in cursor.fetchall()}
        return self._columns_cache

    def _fetch_all(self, query: str, params: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
        with database_manager.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            rows = [dict(row) for row in cursor.fetchall()]
        return rows

    def _fetch_one(self, query: str, params: Optional[Sequence[Any]] = None) -> Optional[Dict[str, Any]]:
        with database_manager.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            row = cursor.fetchone()
        return dict(row) if row else None

    def _execute(
        self,
        query: str,
        params: Optional[Sequence[Any]] = None,
    ) -> int:
        with database_manager.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.lastrowid

    def list_all(self) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {self.table_name} ORDER BY {self.primary_key} DESC"
        return self._fetch_all(query)

    def get_by_id(self, record_id: Any) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
        return self._fetch_one(query, (record_id,))

    def insert(self, payload: Dict[str, Any]) -> int:
        columns = self._fetch_columns()
        filtered_payload: Dict[str, Any] = {
            key: (int(value) if isinstance(value, bool) else value)
            for key, value in payload.items()
            if key in columns
        }
        if not filtered_payload:
            return 0
        columns_clause = ", ".join(filtered_payload.keys())
        placeholders = ", ".join(["?"] * len(filtered_payload))
        query = f"INSERT INTO {self.table_name} ({columns_clause}) VALUES ({placeholders})"
        return self._execute(query, tuple(filtered_payload.values()))

    def update(self, record_id: Any, payload: Dict[str, Any]) -> None:
        columns = self._fetch_columns()
        filtered_payload = {
            key: (int(value) if isinstance(value, bool) else value)
            for key, value in payload.items()
            if key in columns
        }
        if "updated_at" in columns and "updated_at" not in filtered_payload:
            filtered_payload["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
        if not filtered_payload:
            return
        assignments = ", ".join(f"{key} = ?" for key in filtered_payload.keys())
        query = f"UPDATE {self.table_name} SET {assignments} WHERE {self.primary_key} = ?"
        params = tuple(filtered_payload.values()) + (record_id,)
        self._execute(query, params)

    def delete(self, record_id: Any) -> None:
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        self._execute(query, (record_id,))
