from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from ..services.auth import auth_service


class AccountSettingsDialog(QDialog):
    def __init__(self, user: dict, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        self.updated_user: dict | None = None
        self.setWindowTitle("Preferencias da conta")
        self.setModal(True)
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)

        self.username_input = QLineEdit(self.user.get("username", ""))
        self.username_input.setPlaceholderText("Usuario de acesso")
        self.username_input.setToolTip("Defina o usuario utilizado no login.")
        form.addRow("Usuario:", self.username_input)

        self.display_input = QLineEdit(self.user.get("display_name", ""))
        self.display_input.setPlaceholderText("Nome para exibicao")
        self.display_input.setToolTip("Nome mostrado nos avisos e na status bar.")
        form.addRow("Nome exibido:", self.display_input)

        self.current_input = QLineEdit()
        self.current_input.setEchoMode(QLineEdit.Password)
        self.current_input.setPlaceholderText("Senha atual")
        self.current_input.setToolTip("Informe a senha atual para validar as alteracoes.")
        form.addRow("Senha atual:", self.current_input)

        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.Password)
        self.new_input.setPlaceholderText("Nova senha (opcional)")
        self.new_input.setToolTip("Preencha somente se desejar alterar a senha atual.")
        form.addRow("Nova senha:", self.new_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Confirme a nova senha")
        self.confirm_input.setToolTip("Repita a nova senha para confirmacao.")
        form.addRow("Confirmar nova senha:", self.confirm_input)

        layout.addLayout(form)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self._on_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _on_accept(self) -> None:
        username = self.username_input.text().strip()
        display_name = self.display_input.text().strip()
        current_password = self.current_input.text().strip()
        new_password = self.new_input.text().strip()
        confirm_password = self.confirm_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Usuario obrigatorio", "Informe um usuario valido.")
            return

        if not current_password:
            QMessageBox.warning(self, "Senha atual necessaria", "Informe a senha atual para confirmar.")
            return

        if new_password or confirm_password:
            if new_password != confirm_password:
                QMessageBox.warning(self, "Senhas diferentes", "A confirmacao nao confere com a nova senha.")
                return
            if len(new_password) < 3:
                QMessageBox.warning(self, "Senha fraca", "Utilize ao menos 3 caracteres na nova senha.")
                return
        else:
            new_password = None

        if not auth_service.verify_credentials(self.user["username"], current_password):
            QMessageBox.critical(self, "Senha incorreta", "A senha atual informada esta incorreta.")
            return

        try:
            self.updated_user = auth_service.update_profile(
                self.user["id"],
                username,
                display_name or username,
                new_password=new_password,
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Usuario indisponivel", str(exc))
            return

        QMessageBox.information(self, "Sucesso", "Dados atualizados com sucesso.")
        self.accept()
