
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCalendarWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ...services.dashboard import dashboard_service
from ...services.orders import order_service
from ..components.base_page import BasePage


class DashboardPage(BasePage):
    def __init__(self, on_help_requested, on_navigate_to) -> None:
        super().__init__("Resumo Geral", on_help_requested)
        self.on_navigate_to = on_navigate_to
        self._build_content()

    def _build_content(self) -> None:
        layout = self.content_layout

        hero = QLabel("Visao panoramica da oficina")
        hero_font = QFont()
        hero_font.setPointSize(20)
        hero_font.setBold(True)
        hero.setFont(hero_font)
        layout.addWidget(hero)

        caption = QLabel(
            "Indicadores principais e acessos rapidos para comecar o dia."
        )
        caption.setWordWrap(True)
        layout.addWidget(caption)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(18)

        self.metrics = {}
        clients_card = self._create_metric_card("Clientes cadastrados")
        collaborators_card = self._create_metric_card("Colaboradores ativos")
        vehicles_card = self._create_metric_card("Veiculos registrados")
        orders_card = self._create_metric_card("OS em aberto")

        stats_grid.addWidget(clients_card[0], 0, 0)
        stats_grid.addWidget(collaborators_card[0], 0, 1)
        stats_grid.addWidget(vehicles_card[0], 1, 0)
        stats_grid.addWidget(orders_card[0], 1, 1)

        self.metrics["clients"] = clients_card[1]
        self.metrics["collaborators"] = collaborators_card[1]
        self.metrics["vehicles"] = vehicles_card[1]
        self.metrics["open_orders"] = orders_card[1]

        layout.addLayout(stats_grid)

        shortcuts_layout = QHBoxLayout()
        shortcuts_layout.setSpacing(12)

        shortcut_buttons = [
            ("Cadastrar cliente", "clientes"),
            ("Cadastrar veiculo", "veiculos"),
            ("Abrir nova OS", "ordens"),
            ("Equipe da oficina", "colaboradores"),
        ]

        for text, target in shortcut_buttons:
            btn = QPushButton(text)
            btn.setProperty("secondary", "true")
            if target == "ordens":
                btn.setProperty("accent", "true")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, dest=target: self.on_navigate_to(dest))
            shortcuts_layout.addWidget(btn)

        layout.addLayout(shortcuts_layout)

        calendar_layout = QHBoxLayout()
        calendar_layout.setSpacing(20)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.on_calendar_selection)
        calendar_layout.addWidget(self.calendar, stretch=1)

        self.orders_table = QTableWidget(0, 4)
        self.orders_table.setHorizontalHeaderLabels(["Numero OS", "Cliente", "Veiculo", "Status"])
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.orders_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.orders_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        calendar_layout.addWidget(self.orders_table, stretch=2)

        layout.addLayout(calendar_layout)
        self.update_stats()

    def _create_metric_card(self, title: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setProperty("role", "card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 8, 12, 12)
        card_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setProperty("role", "metricTitle")
        card_layout.addWidget(title_label)

        value_label = QLabel("0")
        value_label.setProperty("role", "metricValue")
        card_layout.addWidget(value_label)

        return card, value_label

    def update_stats(self) -> None:
        totals = dashboard_service.get_counts()
        self.metrics["clients"].setText(str(totals["clients"]))
        self.metrics["collaborators"].setText(str(totals["collaborators"]))
        self.metrics["vehicles"].setText(str(totals["vehicles"]))
        self.metrics["open_orders"].setText(str(totals["open_orders"]))
        self.on_calendar_selection()

    def on_calendar_selection(self) -> None:
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        status_labels = {
            "open": "Aberta",
            "in_progress": "Em andamento",
            "waiting_parts": "Aguardando pecas",
            "completed": "Concluida",
            "cancelled": "Cancelada",
        }
        orders = [
            order
            for order in order_service.list_summary()
            if order.get("expected_delivery") == selected_date
        ]
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            data = [
                order.get("order_number", ""),
                order.get("client_name", ""),
                order.get("license_plate", ""),
                status_labels.get(order.get("status"), order.get("status", "")),
            ]
            for col, value in enumerate(data):
                self.orders_table.setItem(row, col, QTableWidgetItem(str(value)))
