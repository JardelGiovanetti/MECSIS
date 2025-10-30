
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services.auth import auth_service
from ..utils.config import resource_path
from .main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MEC-SIS - Acesso")
        self.resize(420, 300)
        icon_path = resource_path("mecsis", "assets", "mecsis.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self._main_window: Optional[MainWindow] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title = QLabel("Acesse o MEC-SIS")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setToolTip("Informe suas credenciais para iniciar o sistema.")
        layout.addWidget(title)

        subtitle = QLabel("Digite usuario e senha cadastrados para continuar.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setToolTip("Usuario fornecido pela administracao.")
        self.username_input.setMaxLength(80)
        self.username_input.setText("123")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setToolTip("Senha segura com letras e numeros.")
        self.password_input.setText("123")
        layout.addWidget(self.password_input)

        self.show_password_check = QCheckBox("Exibir senha")
        self.show_password_check.setToolTip("Marque para visualizar a senha digitada.")
        self.show_password_check.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_check)

        self.login_button = QPushButton("Entrar")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setToolTip("Valida as credenciais informadas e abre o sistema.")
        self.login_button.clicked.connect(self.attempt_login)
        self.login_button.setProperty("accent", "true")
        self.login_button.setDefault(True)
        layout.addWidget(self.login_button)

        layout.addStretch()

        footer = QLabel("Dica: usuario padrao `123`, senha `123`.")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #64748b; font-size: 11px;")
        footer.setToolTip("Credenciais padrao criadas na instalacao inicial.")
        layout.addWidget(footer)

    def toggle_password_visibility(self, state: int) -> None:
        mode = QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)

    def attempt_login(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Campos obrigatorios", "Informe usuario e senha para continuar.")
            return

        user = auth_service.authenticate(username, password)
        if not user:
            QMessageBox.critical(self, "Acesso negado", "Usuario ou senha invalidos. Tente novamente.")
            self.password_input.clear()
            self.password_input.setFocus()
            return

        self.open_main_window(user)

    def open_main_window(self, user: dict) -> None:
        self._main_window = MainWindow(user)
        self._main_window.showMaximized()
        self.close()
