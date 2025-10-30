from __future__ import annotations

from typing import Dict, List, Optional

from .base import BaseService


class VehicleService(BaseService):
    table_name = "vehicles"

    def list_with_relations(self) -> List[Dict]:
        query = (
            "SELECT v.*, c.full_name AS client_name, b.name AS brand_name, m.name AS model_name "
            "FROM vehicles v "
            "JOIN clients c ON c.id = v.client_id "
            "LEFT JOIN brands b ON b.id = v.brand_id "
            "LEFT JOIN vehicle_models m ON m.id = v.model_id "
            "ORDER BY c.full_name, v.license_plate"
        )
        return self._fetch_all(query)

    def list_by_client(self, client_id: int) -> List[Dict]:
        query = (
            "SELECT v.*, b.name AS brand_name, m.name AS model_name "
            "FROM vehicles v "
            "LEFT JOIN brands b ON b.id = v.brand_id "
            "LEFT JOIN vehicle_models m ON m.id = v.model_id "
            "WHERE v.client_id = ? ORDER BY v.license_plate"
        )
        return self._fetch_all(query, (client_id,))

    def find_by_plate(self, license_plate: str) -> Optional[Dict]:
        query = "SELECT * FROM vehicles WHERE license_plate = ?"
        return self._fetch_one(query, (license_plate.upper(),))


vehicle_service = VehicleService()
