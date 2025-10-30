from __future__ import annotations

from typing import Dict, List

from .base import BaseService


class VehicleModelService(BaseService):
    table_name = "vehicle_models"

    def list_with_brand(self) -> List[Dict]:
        query = (
            "SELECT m.id, m.name AS model_name, b.name AS brand_name, m.brand_id "
            "FROM vehicle_models m "
            "JOIN brands b ON b.id = m.brand_id "
            "ORDER BY b.name, m.name"
        )
        return self._fetch_all(query)

    def list_by_brand(self, brand_id: int) -> List[Dict]:
        query = "SELECT * FROM vehicle_models WHERE brand_id = ? ORDER BY name"
        return self._fetch_all(query, (brand_id,))


model_service = VehicleModelService()
