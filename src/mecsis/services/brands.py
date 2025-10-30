from __future__ import annotations

from typing import Dict, List

from .base import BaseService


class BrandService(BaseService):
    table_name = "brands"

    def list_all(self) -> List[Dict]:
        query = "SELECT * FROM brands ORDER BY name"
        return self._fetch_all(query)


brand_service = BrandService()
