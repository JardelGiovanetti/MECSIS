from __future__ import annotations

from typing import Dict, List

from .base import BaseService


class CollaboratorService(BaseService):
    table_name = "collaborators"

    def list_active(self) -> List[Dict]:
        query = "SELECT * FROM collaborators WHERE is_active = 1 ORDER BY full_name"
        return self._fetch_all(query)

    def search(self, keyword: str) -> List[Dict]:
        pattern = f"%{keyword}%"
        query = (
            "SELECT * FROM collaborators "
            "WHERE full_name LIKE ? OR document LIKE ? OR email LIKE ? "
            "ORDER BY full_name"
        )
        return self._fetch_all(query, (pattern, pattern, pattern))


collaborator_service = CollaboratorService()
