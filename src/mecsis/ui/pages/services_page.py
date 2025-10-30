from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QTableWidgetItem,
)

from ...services.services_catalog import service_catalog
from ..components.crud_page import AbstractCrudPage


class ServicesPage(AbstractCrudPage):
    def __init__(self, on_help_requested) -> None:
        columns = [
            ("Servico", "name"),
            ("Preco base", "default_price"),
            ("Duracao (min)", "estimated_duration_minutes"),
            ("Situacao", "is_active"),
        ]
        super().__init__("Servicos", on_help_requested, columns)

    def get_service(self):
        return service_catalog

    def setup_form(self) -> None:
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do servico (ex: Troca de oleo)")
        self.register_field("name", self.name_input, "Nome do servico")

        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText("Descreva o procedimento e detalhes importantes.")
        self.description_input.setFixedHeight(120)
        self.register_field("description", self.description_input, "Descricao")

        self.price_input = QDoubleSpinBox()
        self.price_input.setPrefix("R$ ")
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setSingleStep(5.0)
        self.price_input.setToolTip("Preco base sugerido para este servico.")
        self.register_field("default_price", self.price_input, "Preco base")

        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 1440)
        self.duration_input.setSingleStep(15)
        self.duration_input.setSuffix(" min")
        self.duration_input.setToolTip("Duracao estimada em minutos.")
        self.register_field("estimated_duration_minutes", self.duration_input, "Duracao estimada")

        self.status_combo = QComboBox()
        self.status_combo.addItem("Disponivel", 1)
        self.status_combo.addItem("Indisponivel", 0)
        self.status_combo.setToolTip("Define se o servico aparece para selecao nas Ordens de Servico.")
        self.register_field("is_active", self.status_combo, "Situacao")

    def populate_table(self, records):
        self.table.setRowCount(len(records))
        for row_idx, record in enumerate(records):
            for col_idx, (_, field) in enumerate(self.table_columns):
                if field == "default_price":
                    display = f"R$ {record.get(field, 0):.2f}"
                elif field == "is_active":
                    display = "Disponivel" if record.get(field) else "Indisponivel"
                else:
                    display = record.get(field, "")
                item = QTableWidgetItem(str(display))
                item.setData(Qt.UserRole, record)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

    def collect_form_data(self):
        payload = super().collect_form_data()
        payload["is_active"] = 1 if payload.get("is_active") else 0
        return payload

    def validate_form(self, payload):
        if not payload.get("name"):
            self.status_hint.setText("Informe o nome do servico.")
            return False
        return True
