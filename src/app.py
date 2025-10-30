from __future__ import annotations

import sqlite3
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPalette, QColor
from PySide6.QtWidgets import QApplication, QMessageBox

from mecsis.database.connection import database_manager
from mecsis.ui.login_window import LoginWindow
from mecsis.ui.styles import PALETTE, load_stylesheet
from mecsis.utils.config import resource_path


def configure_palette(app: QApplication) -> None:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(PALETTE.background))
    palette.setColor(QPalette.WindowText, QColor(PALETTE.text_primary))
    palette.setColor(QPalette.Base, QColor(PALETTE.surface_primary))
    palette.setColor(QPalette.AlternateBase, QColor(PALETTE.surface_secondary))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipText, QColor(PALETTE.text_primary))
    palette.setColor(QPalette.Text, QColor(PALETTE.text_primary))
    palette.setColor(QPalette.Button, QColor(PALETTE.surface_primary))
    palette.setColor(QPalette.ButtonText, QColor(PALETTE.text_primary))
    palette.setColor(QPalette.Highlight, QColor(PALETTE.highlight))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)


def main() -> int:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    configure_palette(app)
    app.setStyleSheet(load_stylesheet())

    icon_path = resource_path("mecsis", "assets", "mecsis.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    try:
        database_manager.initialize()
    except sqlite3.Error as exc:
        QMessageBox.critical(
            None,
            "Erro ao preparar dados",
            (
                "Nao foi possivel inicializar o banco local do MEC-SIS.\n"
                "Verifique se voce possui permissao de escrita na pasta do aplicativo.\n\n"
                f"Detalhes tecnicos: {exc}"
            ),
        )
        return 1

    login = LoginWindow()
    login.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
