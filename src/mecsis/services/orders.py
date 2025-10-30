from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from ..database.connection import database_manager
from .base import BaseService


class OrderService(BaseService):
    table_name = "orders"

    def list_summary(self) -> List[Dict[str, Any]]:
        query = (
            "SELECT o.id, o.order_number, o.status, o.summary, o.total_amount, "
            "o.created_at, o.updated_at, o.expected_delivery, "
            "c.full_name AS client_name, v.license_plate, "
            "COALESCE(b.name, '') AS brand_name, COALESCE(m.name, '') AS model_name "
            "FROM orders o "
            "JOIN clients c ON c.id = o.client_id "
            "JOIN vehicles v ON v.id = o.vehicle_id "
            "LEFT JOIN brands b ON b.id = v.brand_id "
            "LEFT JOIN vehicle_models m ON m.id = v.model_id "
            "ORDER BY o.updated_at DESC"
        )
        return self._fetch_all(query)

    def generate_order_number(self) -> str:
        with database_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM orders")
            next_id = cursor.fetchone()[0]
        return f"OS-{datetime.now():%Y}-{int(next_id):05d}"

    def _prepare_order_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prepared = dict(payload)
        prepared.setdefault("labor_cost", 0)
        prepared.setdefault("parts_cost", 0)
        prepared.setdefault("discount", 0)
        prepared.setdefault("total_amount", 0)
        prepared.setdefault("status", "open")
        prepared.setdefault("payment_method", "cash")
        return prepared

    def create_order(
        self,
        payload: Dict[str, Any],
        items: Sequence[Dict[str, Any]],
        collaborator_ids: Sequence[int],
    ) -> int:
        order_payload = self._prepare_order_payload(payload)
        if not order_payload.get("order_number"):
            order_payload["order_number"] = self.generate_order_number()

        with database_manager.get_connection() as conn:
            columns = ", ".join(order_payload.keys())
            placeholders = ", ".join(["?"] * len(order_payload))
            cursor = conn.execute(
                f"INSERT INTO orders ({columns}) VALUES ({placeholders})",
                tuple(order_payload.values()),
            )
            order_id = cursor.lastrowid
            self._replace_items(conn, order_id, items)
            self._replace_collaborators(conn, order_id, collaborator_ids)
            self._recompute_totals(conn, order_id)
        return order_id

    def update_order(
        self,
        order_id: int,
        payload: Dict[str, Any],
        items: Sequence[Dict[str, Any]],
        collaborator_ids: Sequence[int],
    ) -> None:
        order_payload = self._prepare_order_payload(payload)
        if "order_number" in order_payload and not order_payload["order_number"]:
            order_payload["order_number"] = self.generate_order_number()

        order_payload["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
        assignments = ", ".join(f"{key} = ?" for key in order_payload.keys())
        params = tuple(order_payload.values()) + (order_id,)

        with database_manager.get_connection() as conn:
            conn.execute(f"UPDATE orders SET {assignments} WHERE id = ?", params)
            self._replace_items(conn, order_id, items)
            self._replace_collaborators(conn, order_id, collaborator_ids)
            self._recompute_totals(conn, order_id)

    def _replace_items(
        self,
        conn,
        order_id: int,
        items: Sequence[Dict[str, Any]],
    ) -> None:
        conn.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        for item in items:
            qty = max(1, int(item.get("quantity", 1)))
            price = float(item.get("unit_price", 0) or 0)
            discount = float(item.get("discount", 0) or 0)
            total_price = (qty * price) - discount
            conn.execute(
                "INSERT INTO order_items "
                "(order_id, service_id, description, quantity, unit_price, discount, total_price, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    order_id,
                    item.get("service_id"),
                    item.get("description"),
                    qty,
                    price,
                    discount,
                    total_price,
                    item.get("notes"),
                ),
            )

    def _replace_collaborators(
        self,
        conn,
        order_id: int,
        collaborator_ids: Sequence[int],
    ) -> None:
        conn.execute("DELETE FROM order_collaborators WHERE order_id = ?", (order_id,))
        for collaborator_id in collaborator_ids:
            conn.execute(
                "INSERT INTO order_collaborators (order_id, collaborator_id) VALUES (?, ?)",
                (order_id, collaborator_id),
            )

    def get_full_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        order_query = (
            "SELECT o.*, c.full_name AS client_name, v.license_plate, "
            "COALESCE(b.name, '') AS brand_name, COALESCE(m.name, '') AS model_name "
            "FROM orders o "
            "JOIN clients c ON c.id = o.client_id "
            "JOIN vehicles v ON v.id = o.vehicle_id "
            "LEFT JOIN brands b ON b.id = v.brand_id "
            "LEFT JOIN vehicle_models m ON m.id = v.model_id "
            "WHERE o.id = ?"
        )
        order = self._fetch_one(order_query, (order_id,))
        if not order:
            return None

        with database_manager.get_connection() as conn:
            items_cursor = conn.execute(
                "SELECT oi.*, s.name AS service_name "
                "FROM order_items oi "
                "JOIN services s ON s.id = oi.service_id "
                "WHERE oi.order_id = ?",
                (order_id,),
            )
            order["items"] = [dict(row) for row in items_cursor.fetchall()]

            collab_cursor = conn.execute(
                "SELECT oc.collaborator_id, cb.full_name "
                "FROM order_collaborators oc "
                "JOIN collaborators cb ON cb.id = oc.collaborator_id "
                "WHERE oc.order_id = ?",
                (order_id,),
            )
            order["collaborators"] = [dict(row) for row in collab_cursor.fetchall()]

        return order

    def set_status(self, order_id: int, status: str) -> None:
        self._execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))

    def _recompute_totals(self, conn, order_id: int) -> None:
        cursor = conn.execute(
            "SELECT COALESCE(SUM((quantity * unit_price) - discount), 0) AS parts_total "
            "FROM order_items WHERE order_id = ?",
            (order_id,),
        )
        parts_total = float(cursor.fetchone()[0] or 0)

        cursor = conn.execute(
            "SELECT labor_cost, discount FROM orders WHERE id = ?",
            (order_id,),
        )
        row = cursor.fetchone()
        labor_cost = float(row["labor_cost"]) if row and row["labor_cost"] is not None else 0.0
        discount = float(row["discount"]) if row and row["discount"] is not None else 0.0
        total = (labor_cost + parts_total) - discount
        conn.execute(
            "UPDATE orders SET parts_cost = ?, total_amount = ?, updated_at = ? WHERE id = ?",
            (
                parts_total,
                total,
                datetime.utcnow().isoformat(timespec="seconds"),
                order_id,
            ),
        )


order_service = OrderService()
