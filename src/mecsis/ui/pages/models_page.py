from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QLineEdit

from ...services.brands import brand_service
from ...services.models import model_service
from ..components.crud_page import AbstractCrudPage


class ModelsPage(AbstractCrudPage):
    def __init__(self, on_help_requested) -> None:
        columns = [
            ("Marca", "brand_name"),
            ("Modelo", "model_name"),
        ]
        super().__init__("Modelos", on_help_requested, columns)

    def get_service(self):
        return model_service

    def load_records(self, keyword=None):
        return model_service.list_with_brand()

    def setup_form(self) -> None:
        self.brand_combo = QComboBox()
        self.brand_combo.setToolTip("Selecione a marca relacionada a este modelo.")
        self.populate_brands()
        self.register_field("brand_id", self.brand_combo, "Marca")

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Modelo do veiculo (ex: Corolla 2.0)")
        self.model_input.setMaxLength(120)
        self.register_field("name", self.model_input, "Modelo")

    def populate_brands(self) -> None:
        self.brand_combo.clear()
        brands = brand_service.list_all()
        for brand in brands:
            self.brand_combo.addItem(brand["name"], brand["id"])
        if not brands:
            self.brand_combo.addItem("Cadastre uma marca primeiro", None)

    def on_new(self):
        self.populate_brands()
        super().on_new()

    def collect_form_data(self):
        payload = super().collect_form_data()
        payload["brand_id"] = self.brand_combo.currentData()
        return payload

    def populate_form(self, record):
        self.populate_brands()
        super().populate_form(record)

    def validate_form(self, payload):
        if not payload.get("brand_id"):
            self.status_hint.setText("Selecione uma marca.")
            return False
        if not payload.get("name"):
            self.status_hint.setText("Informe o nome do modelo.")
            return False
        return True
