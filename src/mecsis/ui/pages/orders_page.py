from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QPlainTextEdit,
    QWidget,
    QVBoxLayout,
)

from ...services.clients import client_service
from ...services.collaborators import collaborator_service
from ...services.orders import order_service
from ...services.services_catalog import service_catalog
from ...services.vehicles import vehicle_service
from ..components.crud_page import AbstractCrudPage


class OrdersPage(AbstractCrudPage):
    PAYMENT_METHODS = [
        ("PIX", "PIX"),
        ("Dinheiro", "cash"),
        ("Credito", "credit"),
        ("Debito", "debit"),
        ("Transferencia", "transfer"),
        ("Boleto/Faturamento", "invoice"),
    ]

    STATUS_OPTIONS = [
        ("Aberta", "open"),
        ("Em andamento", "in_progress"),
        ("Aguardando pecas", "waiting_parts"),
        ("Concluida", "completed"),
        ("Cancelada", "cancelled"),
    ]

    def __init__(self, on_help_requested) -> None:
        self.current_items: List[Dict] = []
        self.selected_item_index: Optional[int] = None
        self.current_collaborators: List[Dict] = []
        columns = [
            ("No OS", "order_number"),
            ("Cliente", "client_name"),
            ("Veiculo", "license_plate"),
            ("Status", "status"),
            ("Atualizacao", "updated_at"),
            ("Total", "total_amount"),
        ]
        super().__init__("Ordens de Servico", on_help_requested, columns)

    def get_service(self):
        return order_service

    def load_records(self, keyword=None):
        orders = order_service.list_summary()
        if keyword:
            keyword_lower = keyword.lower()
            orders = [
                order
                for order in orders
                if keyword_lower in str(order.get("order_number", "")).lower()
                or keyword_lower in str(order.get("client_name", "")).lower()
                or keyword_lower in str(order.get("license_plate", "")).lower()
            ]
        return orders

    def populate_table(self, records):
        status_labels = {
            "open": "Aberta",
            "in_progress": "Em andamento",
            "waiting_parts": "Aguardando pecas",
            "completed": "Concluida",
            "cancelled": "Cancelada",
        }
        self.table.setRowCount(len(records))
        for row_idx, record in enumerate(records):
            status_display = status_labels.get(record.get("status"), record.get("status", ""))
            updated_at = record.get("updated_at")
            if isinstance(updated_at, datetime):
                updated_display = updated_at.strftime("%d/%m/%Y %H:%M")
            elif updated_at:
                try:
                    updated_display = datetime.fromisoformat(str(updated_at)).strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    updated_display = str(updated_at)
            else:
                updated_display = ""

            total_amount = record.get("total_amount") or 0
            values = [
                record.get("order_number", ""),
                record.get("client_name", ""),
                record.get("license_plate", ""),
                status_display,
                updated_display,
                f"R$ {float(total_amount):.2f}",
            ]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, record)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

    def setup_form(self) -> None:
        self.current_items = []
        self.selected_item_index = None
        self.current_collaborators = []

        self.form_fields.clear()
        self._clear_layout(self.form_layout)
        self.fields_form = QFormLayout()
        self.fields_form.setSpacing(10)
        self.fields_form.setLabelAlignment(Qt.AlignRight)
        self.form_layout.addLayout(self.fields_form)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(16)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Order details section
        details_container = QWidget()
        details_layout = QFormLayout(details_container)
        details_layout.setSpacing(10)

        self.order_number_display = QLabel("Numero sera definido ao salvar")
        self.order_number_display.setToolTip("Identificador unico da OS.")
        details_layout.addRow("Numero:", self.order_number_display)

        self.client_combo = QComboBox()
        self.client_combo.setToolTip("Selecione o cliente para carregar os veiculos disponiveis.")
        self.client_combo.currentIndexChanged.connect(self.on_client_changed)
        self.form_fields["client_id"] = self.client_combo
        details_layout.addRow("Cliente:", self.client_combo)

        self.vehicle_combo = QComboBox()
        self.vehicle_combo.setToolTip("Escolha o veiculo relacionado a OS.")
        details_layout.addRow("Veiculo:", self.vehicle_combo)
        self.form_fields["vehicle_id"] = self.vehicle_combo

        self.responsible_combo = QComboBox()
        self.responsible_combo.setToolTip("Responsavel tecnico pela OS.")
        details_layout.addRow("Responsavel:", self.responsible_combo)
        self.form_fields["responsible_id"] = self.responsible_combo

        self.status_combo = QComboBox()
        self.status_combo.setToolTip("Situacao atual da OS.")
        for label, value in self.STATUS_OPTIONS:
            self.status_combo.addItem(label, value)
        details_layout.addRow("Status:", self.status_combo)
        self.form_fields["status"] = self.status_combo

        self.payment_combo = QComboBox()
        self.payment_combo.setToolTip("Forma de pagamento prevista para o fechamento da OS.")
        for label, value in self.PAYMENT_METHODS:
            self.payment_combo.addItem(label, value)
        details_layout.addRow("Pagamento:", self.payment_combo)
        self.form_fields["payment_method"] = self.payment_combo

        self.summary_input = QLineEdit()
        self.summary_input.setPlaceholderText("Resumo breve da OS")
        details_layout.addRow("Resumo:", self.summary_input)
        self.form_fields["summary"] = self.summary_input

        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText("Descreva o problema relatado, diagnostico e servicos previstos.")
        self.description_input.setFixedHeight(120)
        details_layout.addRow("Descricao:", self.description_input)
        self.form_fields["description"] = self.description_input

        self.expected_date_input = QDateEdit()
        self.expected_date_input.setCalendarPopup(True)
        self.expected_date_input.setDisplayFormat("dd/MM/yyyy")
        details_layout.addRow("Previsao:", self.expected_date_input)
        self.form_fields["expected_delivery"] = self.expected_date_input

        self.labor_input = QDoubleSpinBox()
        self.labor_input.setPrefix("R$ ")
        self.labor_input.setMaximum(999999.99)
        self.labor_input.setDecimals(2)
        self.labor_input.setSingleStep(25.0)
        self.labor_input.setToolTip("Valor estimado de mao de obra.")
        details_layout.addRow("Mao de obra:", self.labor_input)
        self.form_fields["labor_cost"] = self.labor_input
        self.labor_input.valueChanged.connect(self.update_totals_display)

        self.discount_input = QDoubleSpinBox()
        self.discount_input.setPrefix("R$ ")
        self.discount_input.setMaximum(99999.99)
        self.discount_input.setDecimals(2)
        self.discount_input.setSingleStep(10.0)
        self.discount_input.setToolTip("Descontos negociados para esta OS.")
        details_layout.addRow("Desconto:", self.discount_input)
        self.form_fields["discount"] = self.discount_input
        self.discount_input.valueChanged.connect(self.update_totals_display)

        container_layout.addWidget(details_container)

        # Items section
        items_container = QWidget()
        items_layout = QVBoxLayout(items_container)
        items_layout.setSpacing(8)

        items_title = QLabel("Itens de servico / pecas")
        items_title_font = QFont()
        items_title_font.setPointSize(12)
        items_title_font.setBold(True)
        items_title.setFont(items_title_font)
        items_layout.addWidget(items_title)

        self.items_table = self._create_items_table()
        items_layout.addWidget(self.items_table, stretch=1)

        item_form_layout = QHBoxLayout()
        item_form_layout.setSpacing(8)

        self.item_service_combo = QComboBox()
        self.item_service_combo.setMinimumWidth(200)
        self.item_service_combo.setToolTip("Servico ou peca a ser adicionado.")
        item_form_layout.addWidget(self.item_service_combo)

        self.item_description_input = QLineEdit()
        self.item_description_input.setPlaceholderText("Descricao complementar")
        item_form_layout.addWidget(self.item_description_input)

        self.item_quantity_spin = QSpinBox()
        self.item_quantity_spin.setRange(1, 999)
        self.item_quantity_spin.setToolTip("Quantidade aplicada.")
        item_form_layout.addWidget(self.item_quantity_spin)

        self.item_unit_price_spin = QDoubleSpinBox()
        self.item_unit_price_spin.setPrefix("R$ ")
        self.item_unit_price_spin.setMaximum(999999.99)
        self.item_unit_price_spin.setDecimals(2)
        self.item_unit_price_spin.setToolTip("Valor unitario do item.")
        item_form_layout.addWidget(self.item_unit_price_spin)

        self.item_discount_spin = QDoubleSpinBox()
        self.item_discount_spin.setPrefix("R$ ")
        self.item_discount_spin.setMaximum(999999.99)
        self.item_discount_spin.setDecimals(2)
        self.item_discount_spin.setToolTip("Desconto aplicado ao item.")
        item_form_layout.addWidget(self.item_discount_spin)

        items_layout.addLayout(item_form_layout)

        item_buttons_layout = QHBoxLayout()
        item_buttons_layout.setSpacing(8)
        self.add_item_button = QPushButton("Adicionar / Atualizar item")
        self.add_item_button.setCursor(Qt.PointingHandCursor)
        self.add_item_button.setToolTip("Adiciona o item a OS ou atualiza o item selecionado na lista.")
        self.add_item_button.clicked.connect(self.on_add_item)
        item_buttons_layout.addWidget(self.add_item_button)

        self.clear_item_button = QPushButton("Limpar item")
        self.clear_item_button.setCursor(Qt.PointingHandCursor)
        self.clear_item_button.setToolTip("Limpa os campos do item para um novo preenchimento.")
        self.clear_item_button.clicked.connect(self.reset_item_form)
        item_buttons_layout.addWidget(self.clear_item_button)

        self.remove_item_button = QPushButton("Remover item")
        self.remove_item_button.setCursor(Qt.PointingHandCursor)
        self.remove_item_button.setToolTip("Remove o item selecionado da OS.")
        self.remove_item_button.clicked.connect(self.on_remove_item)
        item_buttons_layout.addWidget(self.remove_item_button)
        item_buttons_layout.addStretch()
        items_layout.addLayout(item_buttons_layout)

        # Collaborators section
        collab_title = QLabel("Equipe alocada")
        collab_title_font = QFont()
        collab_title_font.setPointSize(12)
        collab_title_font.setBold(True)
        collab_title.setFont(collab_title_font)
        items_layout.addWidget(collab_title)

        collab_layout = QHBoxLayout()
        collab_layout.setSpacing(8)

        self.collaborator_combo = QComboBox()
        self.collaborator_combo.setToolTip("Selecione colaboradores para alocar nesta OS.")
        collab_layout.addWidget(self.collaborator_combo)

        self.add_collaborator_button = QPushButton("Adicionar colaborador")
        self.add_collaborator_button.setCursor(Qt.PointingHandCursor)
        self.add_collaborator_button.setToolTip("Inclui o colaborador selecionado na lista da OS.")
        self.add_collaborator_button.clicked.connect(self.on_add_collaborator)
        collab_layout.addWidget(self.add_collaborator_button)

        self.remove_collaborator_button = QPushButton("Remover selecionado")
        self.remove_collaborator_button.setCursor(Qt.PointingHandCursor)
        self.remove_collaborator_button.setToolTip("Remove o colaborador selecionado da OS.")
        self.remove_collaborator_button.clicked.connect(self.on_remove_collaborator)
        collab_layout.addWidget(self.remove_collaborator_button)
        items_layout.addLayout(collab_layout)

        self.collaborators_list = QListWidget()
        self.collaborators_list.setToolTip("Colaboradores ja vinculados a ordem de servico.")
        items_layout.addWidget(self.collaborators_list)

        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        self.parts_total_label = QLabel("Pecas/Servicos: R$ 0,00")
        self.parts_total_label.setToolTip("Soma de todos os itens lancados (ja considerando descontos).")
        totals_layout.addWidget(self.parts_total_label)

        self.grand_total_label = QLabel("Total estimado: R$ 0,00")
        self.grand_total_label.setToolTip("Total da OS (mao de obra + itens - desconto).")
        totals_layout.addWidget(self.grand_total_label)
        items_layout.addLayout(totals_layout)

        container_layout.addWidget(items_container)

        self.form_layout.addWidget(container)

        self.populate_clients()
        self.populate_services()
        self.populate_collaborators()
        self.refresh_items_table()
        self.refresh_collaborators_list()

    def _create_items_table(self):
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(["Servico/Peca", "Descricao", "Qtd", "Unitario", "Desconto", "Total"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.itemSelectionChanged.connect(self.on_item_selected)
        table.setToolTip("Itens vinculados a OS. Selecione para editar ou remover.")
        return table

    def populate_clients(self):
        self.client_combo.clear()
        clients = client_service.list_all()
        for client in clients:
            display = f"{client['full_name']} ({client['document']})"
            self.client_combo.addItem(display, client["id"])
        if not clients:
            self.client_combo.addItem("Cadastre clientes antes de criar OS", None)
        self.on_client_changed()

    def populate_services(self):
        self.item_service_combo.clear()
        services = service_catalog.list_active()
        for service in services:
            display = f"{service['name']} (R$ {service['default_price']:.2f})"
            self.item_service_combo.addItem(display, service["id"])
        if not services:
            self.item_service_combo.addItem("Cadastre servicos no catalogo", None)

    def populate_collaborators(self):
        active_collaborators = collaborator_service.list_active()
        self.responsible_combo.clear()
        self.collaborator_combo.clear()
        for collab in active_collaborators:
            self.responsible_combo.addItem(collab["full_name"], collab["id"])
            self.collaborator_combo.addItem(collab["full_name"], collab["id"])
        if not active_collaborators:
            self.responsible_combo.addItem("Cadastre colaboradores", None)
            self.collaborator_combo.addItem("Cadastre colaboradores", None)

    def on_client_changed(self):
        client_id = self.client_combo.currentData()
        self.vehicle_combo.clear()
        if client_id:
            vehicles = vehicle_service.list_by_client(client_id)
            for vehicle in vehicles:
                display = f"{vehicle['license_plate']} - {vehicle.get('brand_name', '')} {vehicle.get('model_name', '')}"
                self.vehicle_combo.addItem(display, vehicle["id"])
            if not vehicles:
                self.vehicle_combo.addItem("Cadastre um veiculo para este cliente", None)
        else:
            self.vehicle_combo.addItem("Selecione um cliente valido", None)

    def on_item_selected(self):
        selected_items = self.items_table.selectedItems()
        if not selected_items:
            self.reset_item_form()
            return
        row = selected_items[0].row()
        self.selected_item_index = row
        item_data = self.current_items[row]
        self.set_combo_by_value(self.item_service_combo, item_data["service_id"])
        self.item_description_input.setText(item_data.get("description", ""))
        self.item_quantity_spin.setValue(int(item_data.get("quantity", 1)))
        self.item_unit_price_spin.setValue(float(item_data.get("unit_price", 0)))
        self.item_discount_spin.setValue(float(item_data.get("discount", 0)))

    def set_combo_by_value(self, combo: QComboBox, value):
        for idx in range(combo.count()):
            if combo.itemData(idx) == value:
                combo.setCurrentIndex(idx)
                return

    def on_add_item(self):
        service_id = self.item_service_combo.currentData()
        if not service_id:
            QMessageBox.warning(self, "Servico obrigatorio", "Selecione um servico/peca antes de adicionar.")
            return
        item = {
            "service_id": service_id,
            "service_name": self.item_service_combo.currentText(),
            "description": self.item_description_input.text().strip(),
            "quantity": self.item_quantity_spin.value(),
            "unit_price": float(self.item_unit_price_spin.value()),
            "discount": float(self.item_discount_spin.value()),
        }
        item["total_price"] = (item["quantity"] * item["unit_price"]) - item["discount"]
        if self.selected_item_index is not None:
            self.current_items[self.selected_item_index] = item
        else:
            self.current_items.append(item)
        self.refresh_items_table()
        self.reset_item_form()

    def on_remove_item(self):
        if self.selected_item_index is None:
            QMessageBox.information(self, "Selecao necessaria", "Escolha um item da lista para remover.")
            return
        self.current_items.pop(self.selected_item_index)
        self.refresh_items_table()
        self.reset_item_form()

    def reset_item_form(self):
        self.selected_item_index = None
        self.item_description_input.clear()
        self.item_quantity_spin.setValue(1)
        self.item_unit_price_spin.setValue(0)
        self.item_discount_spin.setValue(0)
        if self.item_service_combo.count():
            self.item_service_combo.setCurrentIndex(0)
        self.items_table.clearSelection()

    def refresh_items_table(self):
        self.items_table.setRowCount(len(self.current_items))
        for row, item in enumerate(self.current_items):
            values = [
                item.get("service_name", ""),
                item.get("description", ""),
                str(item.get("quantity", 1)),
                f"R$ {item.get('unit_price', 0):.2f}",
                f"R$ {item.get('discount', 0):.2f}",
                f"R$ {item.get('total_price', 0):.2f}",
            ]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                cell.setData(Qt.UserRole, item)
                self.items_table.setItem(row, col, cell)
        self.update_totals_display()

    def update_totals_display(self):
        parts_total = sum(item.get("total_price", 0) for item in self.current_items)
        self.parts_total_label.setText(f"Pecas/Servicos: R$ {parts_total:.2f}")
        total = parts_total + float(self.labor_input.value()) - float(self.discount_input.value())
        self.grand_total_label.setText(f"Total estimado: R$ {total:.2f}")

    def on_add_collaborator(self):
        collaborator_id = self.collaborator_combo.currentData()
        if not collaborator_id:
            return
        if any(c["id"] == collaborator_id for c in self.current_collaborators):
            self.status_hint.setText("Colaborador ja esta alocado nesta OS.")
            return
        name = self.collaborator_combo.currentText()
        self.current_collaborators.append({"id": collaborator_id, "name": name})
        self.refresh_collaborators_list()

    def on_remove_collaborator(self):
        selected = self.collaborators_list.currentItem()
        if not selected:
            return
        collab_id = selected.data(Qt.UserRole)
        self.current_collaborators = [c for c in self.current_collaborators if c["id"] != collab_id]
        self.refresh_collaborators_list()

    def refresh_collaborators_list(self):
        self.collaborators_list.clear()
        for collab in self.current_collaborators:
            item = QListWidgetItem(collab["name"])
            item.setData(Qt.UserRole, collab["id"])
            self.collaborators_list.addItem(item)

    def on_save(self):
        data = self.collect_order_data()
        order_payload = data["order"]
        items = data["items"]
        collaborators = data["collaborators"]
        if not self.validate_order_payload(order_payload):
            return
        if self._current_id:
            order_service.update_order(self._current_id, order_payload, items, collaborators)
            self.status_hint.setText("Ordem de servico atualizada com sucesso.")
        else:
            self._current_id = order_service.create_order(order_payload, items, collaborators)
            self.status_hint.setText("Ordem de servico registrada com sucesso.")
        self.refresh_table()

    def collect_order_data(self):
        expected_delivery = self.expected_date_input.date().toString("yyyy-MM-dd") if self.expected_date_input.date().isValid() else None
        order_payload = {
            "client_id": self.client_combo.currentData(),
            "vehicle_id": self.vehicle_combo.currentData(),
            "responsible_id": self.responsible_combo.currentData(),
            "status": self.status_combo.currentData(),
            "summary": self.summary_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "payment_method": self.payment_combo.currentData(),
            "labor_cost": float(self.labor_input.value()),
            "discount": float(self.discount_input.value()),
            "expected_delivery": expected_delivery,
        }
        return {
            "order": order_payload,
            "items": self.current_items,
            "collaborators": [c["id"] for c in self.current_collaborators],
        }

    def validate_order_payload(self, payload):
        if not payload.get("client_id"):
            self.status_hint.setText("Selecione um cliente para prosseguir.")
            return False
        if not payload.get("vehicle_id"):
            self.status_hint.setText("Selecione um veiculo para vincular a OS.")
            return False
        return True

    def on_delete(self):
        if not self._current_id:
            QMessageBox.information(self, "Selecao necessaria", "Selecione uma OS para excluir.")
            return
        confirmation = QMessageBox.question(
            self,
            "Excluir OS",
            "Tem certeza de que deseja remover esta ordem de servico? Esta acao e irreversivel."
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            order_service.delete(self._current_id)
            self.status_hint.setText("Ordem removida.")
            self.refresh_table()

    def populate_form(self, record):
        full_order = order_service.get_full_order(record["id"])
        if not full_order:
            return
        self.populate_clients()
        self.populate_services()
        self.populate_collaborators()

        client_id = full_order.get("client_id")
        self.set_combo_by_value(self.client_combo, client_id)
        self.on_client_changed()
        self.set_combo_by_value(self.vehicle_combo, full_order.get("vehicle_id"))
        self.set_combo_by_value(self.responsible_combo, full_order.get("responsible_id"))
        self.set_combo_by_value(self.status_combo, full_order.get("status"))
        self.set_combo_by_value(self.payment_combo, full_order.get("payment_method"))

        self.summary_input.setText(full_order.get("summary", "") or "")
        self.description_input.setPlainText(full_order.get("description", "") or "")
        if full_order.get("expected_delivery"):
            self.expected_date_input.setDate(QDate.fromString(full_order["expected_delivery"], "yyyy-MM-dd"))
        self.labor_input.setValue(float(full_order.get("labor_cost", 0)))
        self.discount_input.setValue(float(full_order.get("discount", 0)))

        self.current_items = []
        for item in full_order.get("items", []):
            prepared = {
                "service_id": item["service_id"],
                "service_name": item.get("service_name"),
                "description": item.get("description"),
                "quantity": item.get("quantity", 1),
                "unit_price": float(item.get("unit_price", 0)),
                "discount": float(item.get("discount", 0)),
                "total_price": float(item.get("total_price", 0)),
                "notes": item.get("notes"),
            }
            self.current_items.append(prepared)
        self.refresh_items_table()

        self.current_collaborators = [
            {"id": collab["collaborator_id"], "name": collab["full_name"]}
            for collab in full_order.get("collaborators", [])
        ]
        self.refresh_collaborators_list()
        self._current_id = full_order["id"]
        self.order_number_display.setText(full_order.get("order_number", ""))
        self.status_hint.setText("OS carregada. Ajuste e salve para manter os registros atualizados.")

    def reset_form(self):
        super().reset_form()
        self.populate_clients()
        self.populate_services()
        self.populate_collaborators()
        self.summary_input.clear()
        self.description_input.clear()
        self.expected_date_input.setDate(QDate.currentDate())
        self.labor_input.setValue(0)
        self.discount_input.setValue(0)
        self.current_items = []
        self.current_collaborators = []
        self.refresh_items_table()
        self.refresh_collaborators_list()
        if hasattr(self, "order_number_display"):
            self.order_number_display.setText("Numero sera definido ao salvar")

    def _clear_layout(self, layout: QLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.deleteLater()
            if child_layout:
                self._clear_layout(child_layout)  # type: ignore[arg-type]
