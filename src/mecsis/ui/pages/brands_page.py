from __future__ import annotations

from PySide6.QtWidgets import QLineEdit

from ...services.brands import brand_service
from ..components.crud_page import AbstractCrudPage


class BrandsPage(AbstractCrudPage):
    def __init__(self, on_help_requested) -> None:
        columns = [("Marca", "name")]
        super().__init__("Marcas", on_help_requested, columns)

    def get_service(self):
        return brand_service

    def setup_form(self) -> None:
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Toyota, Ford, Volkswagen...")
        self.name_input.setMaxLength(120)
        self.register_field("name", self.name_input, "Nome da marca")

    def validate_form(self, payload):
        if not payload.get("name"):
            self.status_hint.setText("Informe o nome da marca.")
            return False
        return True
