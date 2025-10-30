from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .base_page import BasePage


class AbstractCrudPage(BasePage):
    def __init__(
        self,
        title: str,
        on_help_requested,
        table_columns: Sequence[Tuple[str, str]],
    ) -> None:
        super().__init__(title, on_help_requested)
        self.table_columns = list(table_columns)
        self._current_id: Optional[int] = None
        self.form_fields: Dict[str, QWidget] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        body_layout = self.content_layout

        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar os registros...")
        self.search_input.setToolTip("Pesquise por qualquer informacao relevante e pressione Enter.")
        self.search_input.returnPressed.connect(self.on_search)

        self.search_button = QPushButton("Buscar")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.setToolTip("Executa a pesquisa com o termo informado.")
        self.search_button.clicked.connect(self.on_search)

        self.reset_button = QPushButton("Limpar busca")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setToolTip("Limpa o campo de busca e recarrega todos os dados.")
        self.reset_button.clicked.connect(self.on_reset_search)

        search_layout.addWidget(self.search_input, stretch=2)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reset_button)
        body_layout.addLayout(search_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        body_layout.addLayout(content_layout, stretch=1)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.table_columns))
        self.table.setHorizontalHeaderLabels([col[0] for col in self.table_columns])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setToolTip("Lista de registros. Clique para carregar os detalhes no formulario ao lado.")
        self.table.itemSelectionChanged.connect(self.on_table_selection)

        content_layout.addWidget(self.table, stretch=3)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(12, 12, 12, 12)

        form_title = QLabel("Detalhes")
        form_title_font = QFont()
        form_title_font.setPointSize(14)
        form_title_font.setBold(True)
        form_title.setFont(form_title_font)
        form_title.setToolTip("Area de edicao do registro selecionado.")
        form_layout.addWidget(form_title)

        self.form_scroll = QScrollArea()
        self.form_scroll.setWidgetResizable(True)
        self.form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(12)

        self.fields_form = QFormLayout()
        self.fields_form.setSpacing(10)
        self.fields_form.setLabelAlignment(Qt.AlignRight)
        self.form_layout.addLayout(self.fields_form)

        self.form_scroll.setWidget(self.form_widget)
        form_layout.addWidget(self.form_scroll, stretch=1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.new_button = QPushButton("Novo")
        self.new_button.setCursor(Qt.PointingHandCursor)
        self.new_button.setToolTip("Limpa o formulario para inclusao de um novo registro.")
        self.new_button.clicked.connect(self.on_new)

        self.save_button = QPushButton("Salvar")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setToolTip("Salva as informacoes preenchidas no formulario.")
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setDefault(True)

        self.delete_button = QPushButton("Excluir")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setToolTip("Remove o registro selecionado permanentemente.")
        self.delete_button.clicked.connect(self.on_delete)

        buttons_layout.addWidget(self.new_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()

        self.form_layout.addLayout(buttons_layout)

        content_layout.addWidget(form_container, stretch=2)
        self.status_hint = QLabel("Selecione um item ou utilize os botoes acima para comecar.")
        self.status_hint.setObjectName("statusHint")
        self.status_hint.setWordWrap(True)
        self.status_hint.setToolTip("Mensagens rapidas sobre o que fazer na tela atual.")
        body_layout.addWidget(self.status_hint)

        self.setup_form()
        self.refresh_table()

    def setup_form(self) -> None:
        raise NotImplementedError("setup_form needs to be implemented by subclasses.")

    def get_service(self):
        raise NotImplementedError("get_service needs to be implemented by subclasses.")

    def on_search(self) -> None:
        keyword = self.search_input.text().strip()
        if keyword:
            results = self.perform_search(keyword)
        else:
            results = self.load_records()
        self.populate_table(results)

    def perform_search(self, keyword: str) -> List[Dict[str, Any]]:
        return self.load_records(keyword)

    def on_reset_search(self) -> None:
        self.search_input.clear()
        self.refresh_table()

    def refresh_table(self) -> None:
        records = self.load_records()
        self.populate_table(records)
        self.reset_form()

    def load_records(self, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        service = self.get_service()
        if keyword and hasattr(service, "search"):
            return service.search(keyword)
        if hasattr(service, "list_with_relations"):
            return service.list_with_relations()
        return service.list_all()

    def populate_table(self, records: Sequence[Dict[str, Any]]) -> None:
        self.table.setRowCount(len(records))
        for row_idx, record in enumerate(records):
            for col_idx, (_, field) in enumerate(self.table_columns):
                value = record.get(field, "")
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setData(Qt.UserRole, record)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

    def on_table_selection(self) -> None:
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        record = selected_items[0].data(Qt.UserRole)
        if record:
            self._current_id = record.get("id")
            self.populate_form(record)
            self.status_hint.setText("Registro carregado. Ajuste os dados e clique em Salvar.")

    def populate_form(self, record: Dict[str, Any]) -> None:
        for field_name, widget in self.form_fields.items():
            value = record.get(field_name)
            self.set_widget_value(widget, value)

    def reset_form(self) -> None:
        self._current_id = None
        for widget in self.form_fields.values():
            self.set_widget_value(widget, None)
        self.status_hint.setText("Pronto para criar um novo registro.")

    def on_new(self) -> None:
        self.reset_form()
        self.table.clearSelection()

    def on_save(self) -> None:
        payload = self.collect_form_data()
        if not self.validate_form(payload):
            return
        service = self.get_service()
        if self._current_id:
            service.update(self._current_id, payload)
            self.status_hint.setText("Atualizacao concluida com sucesso.")
        else:
            self._current_id = service.insert(payload)
            self.status_hint.setText("Cadastro realizado com sucesso.")
        self.refresh_table()

    def on_delete(self) -> None:
        if not self._current_id:
            QMessageBox.information(self, "Selecao necessaria", "Selecione um registro para excluir.")
            return
        confirmation = QMessageBox.question(
            self,
            "Confirmacao",
            "Tem certeza de que deseja remover este registro?",
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            service = self.get_service()
            service.delete(self._current_id)
            self.status_hint.setText("Registro excluido.")
            self.refresh_table()

    def collect_form_data(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        for field_name, widget in self.form_fields.items():
            payload[field_name] = self.get_widget_value(widget)
        return payload

    def validate_form(self, payload: Dict[str, Any]) -> bool:
        return True

    # Helper methods to interact with widgets
    def register_field(self, field_name: str, widget: QWidget, label: str) -> None:
        widget.setObjectName(field_name)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        widget.setToolTip(f"Informe {label.lower()}.")
        self.form_fields[field_name] = widget
        self.fields_form.addRow(label + ":", widget)

    def get_widget_value(self, widget: QWidget) -> Any:
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        if isinstance(widget, QPlainTextEdit):
            return widget.toPlainText().strip()
        if isinstance(widget, QComboBox):
            return widget.currentData()
        if isinstance(widget, QSpinBox):
            return widget.value()
        if isinstance(widget, QDoubleSpinBox):
            return float(widget.value())
        if isinstance(widget, QDateEdit):
            return widget.date().toString("yyyy-MM-dd")
        return None

    def set_widget_value(self, widget: QWidget, value: Any) -> None:
        if isinstance(widget, QLineEdit):
            widget.setText("" if value is None else str(value))
        elif isinstance(widget, QPlainTextEdit):
            widget.setPlainText("" if value is None else str(value))
        elif isinstance(widget, QComboBox):
            for idx in range(widget.count()):
                if widget.itemData(idx) == value:
                    widget.setCurrentIndex(idx)
                    return
            if widget.count():
                widget.setCurrentIndex(0)
        elif isinstance(widget, QSpinBox):
            if value is not None:
                widget.setValue(int(value))
            else:
                widget.setValue(widget.minimum())
        elif isinstance(widget, QDoubleSpinBox):
            if value is not None:
                widget.setValue(float(value))
            else:
                widget.setValue(widget.minimum())
        elif isinstance(widget, QDateEdit):
            if value:
                widget.setDate(widget.date().fromString(str(value), "yyyy-MM-dd"))
        elif hasattr(widget, "setCurrentIndex"):
            options = getattr(widget, "count", lambda: 0)()
            for idx in range(options):
                if getattr(widget, "itemData")(idx) == value:
                    widget.setCurrentIndex(idx)
                    return
            if options:
                widget.setCurrentIndex(0)
