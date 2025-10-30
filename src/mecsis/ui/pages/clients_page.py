from __future__ import annotations

from PySide6.QtWidgets import QLineEdit, QPlainTextEdit

from ...services.clients import client_service
from ..components.crud_page import AbstractCrudPage


class ClientsPage(AbstractCrudPage):
    def __init__(self, on_help_requested) -> None:
        columns = [
            ("Nome", "full_name"),
            ("Documento", "document"),
            ("Telefone", "phone"),
            ("Celular", "mobile"),
            ("Cidade", "city"),
        ]
        super().__init__("Clientes", on_help_requested, columns)

    def get_service(self):
        return client_service

    def setup_form(self) -> None:
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome completo do cliente")
        self.name_input.setMaxLength(180)
        self.register_field("full_name", self.name_input, "Nome completo")

        self.document_input = QLineEdit()
        self.document_input.setPlaceholderText("CPF ou CNPJ")
        self.document_input.setMaxLength(20)
        self.register_field("document", self.document_input, "Documento")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-mail principal")
        self.register_field("email", self.email_input, "E-mail")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Telefone fixo")
        self.register_field("phone", self.phone_input, "Telefone")

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Celular / WhatsApp")
        self.register_field("mobile", self.mobile_input, "Celular")

        self.zip_input = QLineEdit()
        self.zip_input.setPlaceholderText("CEP")
        self.zip_input.setMaxLength(10)
        self.register_field("zip_code", self.zip_input, "CEP")

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Logradouro")
        self.register_field("address_line", self.address_input, "Endereco")

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Numero")
        self.number_input.setMaxLength(12)
        self.register_field("number", self.number_input, "Numero")

        self.complement_input = QLineEdit()
        self.complement_input.setPlaceholderText("Complemento")
        self.register_field("complement", self.complement_input, "Complemento")

        self.district_input = QLineEdit()
        self.district_input.setPlaceholderText("Bairro")
        self.register_field("district", self.district_input, "Bairro")

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Cidade")
        self.register_field("city", self.city_input, "Cidade")

        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText("UF")
        self.state_input.setMaxLength(2)
        self.register_field("state", self.state_input, "Estado")

        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("Observacoes gerais sobre o cliente")
        self.notes_input.setFixedHeight(100)
        self.register_field("notes", self.notes_input, "Observacoes")

    def validate_form(self, payload):
        if not payload.get("full_name"):
            self.status_hint.setText("Informe o nome do cliente.")
            return False
        if not payload.get("document"):
            self.status_hint.setText("Informe o documento do cliente.")
            return False
        return True
