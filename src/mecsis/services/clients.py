from __future__ import annotations

from typing import Dict, List, Optional

from .base import BaseService


class ClientService(BaseService):
    table_name = "clients"

    def search(self, keyword: str) -> List[Dict]:
        pattern = f"%{keyword}%"
        query = (
            "SELECT * FROM clients "
            "WHERE full_name LIKE ? OR document LIKE ? OR phone LIKE ? OR mobile LIKE ? "
            "ORDER BY full_name"
        )
        return self._fetch_all(query, (pattern, pattern, pattern, pattern))

    def get_summary(self, client_id: int) -> Optional[Dict]:
        query = (
            "SELECT c.*, "
            "(SELECT COUNT(*) FROM vehicles v WHERE v.client_id = c.id) AS vehicle_count, "
            "(SELECT COUNT(*) FROM orders o WHERE o.client_id = c.id) AS order_count "
            "FROM clients c WHERE c.id = ?"
        )
        return self._fetch_one(query, (client_id,))


client_service = ClientService()
