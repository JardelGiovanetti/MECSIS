from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QStyle,
)


class BasePage(QWidget):
    def __init__(self, title: str, on_help_requested: Callable[[], None]) -> None:
        super().__init__()
        self.on_help_requested = on_help_requested
        self.setObjectName("pageContainer")
        self._build_header(title)

    def _build_header(self, title: str) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setObjectName("pageTitle")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setToolTip(f"Area atual: {title}")

        help_button = QPushButton("Ajuda")
        help_button.setObjectName("helpButton")
        help_button.setCursor(Qt.PointingHandCursor)
        help_button.setFixedHeight(32)
        help_button.setIcon(self.style().standardIcon(QStyle.SP_DialogHelpButton))
        help_button.setToolTip("Clique para abrir a central de ajuda do MEC-SIS.")
        help_button.clicked.connect(self.on_help_requested)

        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(help_button)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: #cccccc;")

        root_layout.addLayout(header)
        root_layout.addWidget(divider)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        root_layout.addWidget(content_widget)
        self._content_layout = content_layout

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout
