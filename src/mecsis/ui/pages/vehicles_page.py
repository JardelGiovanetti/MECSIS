from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QTableWidgetItem,
)

from ...services.brands import brand_service
from ...services.clients import client_service
from ...services.models import model_service
from ...services.vehicles import vehicle_service
from ..components.crud_page import AbstractCrudPage


class VehiclesPage(AbstractCrudPage):
    def __init__(self, on_help_requested) -> None:
        columns = [
            ("Cliente", "client_name"),
            ("Placa", "license_plate"),
            ("Marca", "brand_name"),
            ("Modelo", "model_name"),
            ("Ano", "model_year"),
        ]
        super().__init__("Veiculos", on_help_requested, columns)

    def get_service(self):
        return vehicle_service

    def load_records(self, keyword=None):
        return vehicle_service.list_with_relations()

    def setup_form(self) -> None:
        self.client_combo = QComboBox()
        self.client_combo.setToolTip("Selecione o cliente proprietario do veiculo.")
        self.register_field("client_id", self.client_combo, "Cliente")

        self.brand_combo = QComboBox()
        self.brand_combo.setToolTip("Escolha a marca do veiculo.")
        self.brand_combo.currentIndexChanged.connect(self.on_brand_changed)
        self.register_field("brand_id", self.brand_combo, "Marca")

        self.model_combo = QComboBox()
        self.model_combo.setToolTip("Escolha o modelo correspondente a marca.")
        self.register_field("model_id", self.model_combo, "Modelo")

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("ABC1D23")
        self.license_input.setMaxLength(8)
        self.register_field("license_plate", self.license_input, "Placa")

        self.vin_input = QLineEdit()
        self.vin_input.setPlaceholderText("Numero do chassi")
        self.vin_input.setMaxLength(30)
        self.register_field("vin", self.vin_input, "Chassi/VIN")

        self.manufacture_year_input = QSpinBox()
        self.manufacture_year_input.setRange(1960, 2100)
        self.manufacture_year_input.setSuffix(" (fabr.)")
        self.register_field("manufacture_year", self.manufacture_year_input, "Ano fabricacao")

        self.model_year_input = QSpinBox()
        self.model_year_input.setRange(1960, 2100)
        self.model_year_input.setSuffix(" (modelo)")
        self.register_field("model_year", self.model_year_input, "Ano modelo")

        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Cor predominante")
        self.register_field("color", self.color_input, "Cor")

        self.fuel_input = QLineEdit()
        self.fuel_input.setPlaceholderText("Tipo de combustivel")
        self.register_field("fuel_type", self.fuel_input, "Combustivel")

        self.mileage_input = QSpinBox()
        self.mileage_input.setRange(0, 2000000)
        self.mileage_input.setSingleStep(1000)
        self.mileage_input.setSuffix(" km")
        self.register_field("mileage", self.mileage_input, "Quilometragem")

        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("Observacoes sobre o veiculo, revisoes, restricoes etc.")
        self.notes_input.setFixedHeight(100)
        self.register_field("notes", self.notes_input, "Observacoes")

        self.populate_clients()
        self.populate_brands()
        self.populate_models()

    def populate_clients(self):
        self.client_combo.clear()
        clients = client_service.list_all()
        for client in clients:
            self.client_combo.addItem(client["full_name"], client["id"])
        if not clients:
            self.client_combo.addItem("Cadastre um cliente primeiro", None)

    def populate_brands(self):
        self.brand_combo.clear()
        brands = brand_service.list_all()
        for brand in brands:
            self.brand_combo.addItem(brand["name"], brand["id"])
        if not brands:
            self.brand_combo.addItem("Cadastre uma marca primeiro", None)

    def populate_models(self, brand_id: int | None = None):
        self.model_combo.clear()
        if brand_id:
            models = model_service.list_by_brand(brand_id)
        else:
            models = []
        for model in models:
            self.model_combo.addItem(model["name"], model["id"])
        if not models:
            self.model_combo.addItem("Cadastre um modelo para esta marca", None)

    def on_brand_changed(self):
        brand_id = self.brand_combo.currentData()
        if brand_id:
            self.populate_models(brand_id)
        else:
            self.populate_models(None)

    def on_new(self):
        self.populate_clients()
        self.populate_brands()
        current_brand = self.brand_combo.currentData()
        self.populate_models(current_brand)
        super().on_new()

    def populate_form(self, record):
        self.populate_clients()
        self.populate_brands()
        brand_id = record.get("brand_id")
        self.populate_models(brand_id)
        super().populate_form(record)

    def collect_form_data(self):
        payload = super().collect_form_data()
        payload["client_id"] = self.client_combo.currentData()
        payload["brand_id"] = self.brand_combo.currentData()
        payload["model_id"] = self.model_combo.currentData()
        if payload.get("license_plate"):
            payload["license_plate"] = payload["license_plate"].replace(" ", "").upper()
        return payload

    def validate_form(self, payload):
        if not payload.get("client_id"):
            self.status_hint.setText("Selecione um cliente.")
            return False
        if not payload.get("license_plate"):
            self.status_hint.setText("Informe a placa do veiculo.")
            return False
        return True

    def populate_table(self, records):
        self.table.setRowCount(len(records))
        for row_idx, record in enumerate(records):
            for col_idx, (_, field) in enumerate(self.table_columns):
                display = record.get(field, "")
                item = QTableWidgetItem(str(display) if display is not None else "")
                item.setData(Qt.UserRole, record)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()
