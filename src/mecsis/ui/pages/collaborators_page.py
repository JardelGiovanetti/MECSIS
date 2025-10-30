from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QLineEdit, QTableWidgetItem

from ...services.collaborators import collaborator_service
from ..components.crud_page import AbstractCrudPage


class CollaboratorsPage(AbstractCrudPage):
    def __init__(self, on_help_requested) -> None:
        columns = [
            ("Nome", "full_name"),
            ("Documento", "document"),
            ("Cargo", "position_title"),
            ("Contato", "phone"),
            ("Situacao", "is_active"),
        ]
        super().__init__("Colaboradores", on_help_requested, columns)

    def get_service(self):
        return collaborator_service

    def setup_form(self) -> None:
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome completo do colaborador")
        self.register_field("full_name", self.name_input, "Nome completo")

        self.document_input = QLineEdit()
        self.document_input.setPlaceholderText("CPF")
        self.register_field("document", self.document_input, "Documento")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-mail corporativo ou pessoal")
        self.register_field("email", self.email_input, "E-mail")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Telefone ou celular principal")
        self.register_field("phone", self.phone_input, "Telefone")

        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Funcao ou cargo")
        self.register_field("position_title", self.position_input, "Cargo/Funcao")

        self.rate_input = QDoubleSpinBox()
        self.rate_input.setPrefix("R$ ")
        self.rate_input.setMaximum(9999.99)
        self.rate_input.setDecimals(2)
        self.rate_input.setSingleStep(10.0)
        self.rate_input.setToolTip("Valor padrao de mao de obra por hora deste colaborador.")
        self.register_field("labor_rate", self.rate_input, "Valor hora")

        self.status_combo = QComboBox()
        self.status_combo.addItem("Ativo", 1)
        self.status_combo.addItem("Inativo", 0)
        self.status_combo.setToolTip("Define se o colaborador pode ser alocado em Ordens de Servico.")
        self.register_field("is_active", self.status_combo, "Situacao")

    def populate_table(self, records):
        self.table.setRowCount(len(records))
        for row_idx, record in enumerate(records):
            for col_idx, (_, field) in enumerate(self.table_columns):
                if field == "is_active":
                    display = "Ativo" if record.get(field) else "Inativo"
                else:
                    display = record.get(field, "")
                item = QTableWidgetItem(str(display) if display is not None else "")
                item.setData(Qt.UserRole, record)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

    def collect_form_data(self):
        payload = super().collect_form_data()
        payload["is_active"] = 1 if payload.get("is_active") else 0
        return payload

    def validate_form(self, payload):
        if not payload.get("full_name"):
            self.status_hint.setText("Informe o nome do colaborador.")
            return False
        return True
