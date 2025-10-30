from __future__ import annotations

from typing import Dict

from ..database.connection import database_manager


class DashboardService:
    def get_counts(self) -> Dict[str, int]:
        with database_manager.get_connection() as conn:
            clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            collaborators = conn.execute(
                "SELECT COUNT(*) FROM collaborators WHERE is_active = 1"
            ).fetchone()[0]
            vehicles = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
            open_orders = conn.execute(
                "SELECT COUNT(*) FROM orders WHERE status IN ('open', 'in_progress', 'waiting_parts')"
            ).fetchone()[0]
        return {
            "clients": clients,
            "collaborators": collaborators,
            "vehicles": vehicles,
            "open_orders": open_orders,
        }


dashboard_service = DashboardService()
