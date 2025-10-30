
from __future__ import annotations

from typing import Dict

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..utils.config import resource_path
from .dialogs import AccountSettingsDialog
from .pages.brands_page import BrandsPage
from .pages.clients_page import ClientsPage
from .pages.collaborators_page import CollaboratorsPage
from .pages.dashboard_page import DashboardPage
from .pages.help_page import HelpPage
from .pages.models_page import ModelsPage
from .pages.orders_page import OrdersPage
from .pages.services_page import ServicesPage
from .pages.vehicles_page import VehiclesPage


class MainWindow(QMainWindow):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.user = user
        self.setWindowTitle("MEC-SIS - Gestao de Oficina")
        icon_path = resource_path("mecsis", "assets", "mecsis.ico")
        if icon_path.exists():
            app_icon = QIcon(str(icon_path))
            self.setWindowIcon(app_icon)
        self.resize(1400, 860)
        self.pages: Dict[str, QWidget] = {}
        self.nav_buttons: Dict[str, QPushButton] = {}
        self._build_ui()
        self.statusBar().showMessage(
            f"Usuario autenticado: {user.get('display_name', user.get('username'))}"
        )

    def _build_ui(self) -> None:
        container = QWidget()
        root_layout = QHBoxLayout(container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(24)

        navigation = self._build_navigation()
        root_layout.addWidget(navigation, stretch=0)

        self.stack = QStackedWidget()
        self.stack.setContentsMargins(24, 32, 24, 24)
        root_layout.addWidget(self.stack, stretch=1)
        self.setCentralWidget(container)

        self._register_pages()
        self._build_toolbar()
        self.navigate_to("dashboard")

    def _build_navigation(self) -> QFrame:
        nav_frame = QFrame()
        nav_frame.setObjectName("navigationPanel")
        nav_frame.setFixedWidth(240)
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(24, 36, 24, 36)
        nav_layout.setSpacing(16)

        logo = QLabel("MEC-SIS")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 28px; font-weight: 800; letter-spacing: 0.32em;")
        logo.setToolTip("Sistema integrado para gestao de oficina mecanica")
        nav_layout.addWidget(logo)

        subtitle = QLabel("Navegacao")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748b; text-transform: uppercase; letter-spacing: 0.28em;")
        nav_layout.addWidget(subtitle)

        nav_layout.addSpacing(12)

        items = [
            ("dashboard", "Painel"),
            ("clientes", "Clientes"),
            ("veiculos", "Veiculos"),
            ("colaboradores", "Colaboradores"),
            ("servicos", "Servicos"),
            ("ordens", "Ordens de servico"),
            ("marcas", "Marcas"),
            ("modelos", "Modelos"),
            ("ajuda", "Ajuda"),
        ]

        for key, label in items:
            button = QPushButton(label)
            button.setCheckable(True)
            button.setProperty("secondary", "true")
            button.setProperty("accent", "false")
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(f"Ir para a area de {label}.")
            button.clicked.connect(lambda _, k=key: self.navigate_to(k))
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.setStyleSheet(
                "QPushButton { text-align: left; padding: 12px 18px; font-size: 15px; }"
            )
            self.nav_buttons[key] = button
            nav_layout.addWidget(button)

        nav_layout.addStretch(1)

        version_label = QLabel("Versao 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #64748b; font-size: 11px;")
        version_label.setToolTip("Versao atual do MEC-SIS")
        nav_layout.addWidget(version_label)

        return nav_frame

    def _register_pages(self) -> None:
        self.pages["dashboard"] = DashboardPage(self.show_help, self.navigate_to)
        self.pages["clientes"] = ClientsPage(self.show_help)
        self.pages["colaboradores"] = CollaboratorsPage(self.show_help)
        self.pages["veiculos"] = VehiclesPage(self.show_help)
        self.pages["servicos"] = ServicesPage(self.show_help)
        self.pages["ordens"] = OrdersPage(self.show_help)
        self.pages["marcas"] = BrandsPage(self.show_help)
        self.pages["modelos"] = ModelsPage(self.show_help)
        self.pages["ajuda"] = HelpPage(self.show_help)

        for page in self.pages.values():
            self.stack.addWidget(page)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Comandos")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        refresh_action = QAction("Atualizar", self)
        refresh_action.setToolTip("Recarrega as informacoes da tela atual.")
        refresh_action.triggered.connect(self.refresh_current_page)
        toolbar.addAction(refresh_action)

        fullscreen_action = QAction("Tela cheia", self)
        fullscreen_action.setToolTip("Alterna entre janela e tela cheia (F11).")
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        toolbar.addAction(fullscreen_action)

        account_action = QAction("Minha conta", self)
        account_action.setToolTip("Atualiza usuario, nome de exibicao e senha.")
        account_action.triggered.connect(self.open_account_dialog)
        toolbar.addAction(account_action)

        toolbar.addSeparator()

        logout_action = QAction("Encerrar sessao", self)
        logout_action.triggered.connect(self.close)
        toolbar.addAction(logout_action)

    def toggle_fullscreen(self) -> None:
        if self.windowState() & Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()

    def open_account_dialog(self) -> None:
        dialog = AccountSettingsDialog(self.user, self)
        if dialog.exec() == QDialog.Accepted and dialog.updated_user:
            self.user = dialog.updated_user
            self.statusBar().showMessage(
                f"Usuario autenticado: {self.user.get('display_name', self.user.get('username'))}"
            )

    def navigate_to(self, key: str) -> None:
        if key not in self.pages:
            return
        page = self.pages[key]
        index = self.stack.indexOf(page)
        if index == -1:
            return
        self.stack.setCurrentIndex(index)
        self.highlight_navigation(key)
        self.refresh_page(page)
        self.statusBar().showMessage(f"Visualizando: {self.nav_buttons[key].text()}")

    def highlight_navigation(self, active_key: str) -> None:
        for key, button in self.nav_buttons.items():
            button.setChecked(key == active_key)
            button.setProperty("accent", "true" if key == active_key else "false")
            button.style().unpolish(button)
            button.style().polish(button)

    def refresh_page(self, page: QWidget) -> None:
        if hasattr(page, "refresh_table"):
            page.refresh_table()
        elif hasattr(page, "update_stats"):
            page.update_stats()

    def refresh_current_page(self) -> None:
        current = self.stack.currentWidget()
        if current:
            self.refresh_page(current)

    def show_help(self) -> None:
        self.navigate_to("ajuda")
