from __future__ import annotations

from typing import Dict, List

from .base import BaseService


class ServiceCatalog(BaseService):
    table_name = "services"

    def list_active(self) -> List[Dict]:
        query = "SELECT * FROM services WHERE is_active = 1 ORDER BY name"
        return self._fetch_all(query)


service_catalog = ServiceCatalog()
