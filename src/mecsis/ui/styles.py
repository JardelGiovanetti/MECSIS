from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    background: str = "#f5f7fb"
    surface_primary: str = "#ffffff"
    surface_secondary: str = "#f1f4fb"
    card_background: str = "#ffffff"
    highlight: str = "#2563eb"
    highlight_soft: str = "#3b82f6"
    text_primary: str = "#1f2937"
    text_secondary: str = "#64748b"
    border: str = "#d6deeb"
    danger: str = "#dc2626"
    success: str = "#16a34a"


PALETTE = Palette()


def load_stylesheet() -> str:
    return f"""
        * {{
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            color: {PALETTE.text_primary};
        }}

        QWidget {{
            background-color: {PALETTE.background};
        }}

        QToolTip {{
            background-color: #ffffff;
            color: {PALETTE.text_primary};
            border: 1px solid {PALETTE.highlight};
            padding: 6px;
            border-radius: 6px;
        }}

        QFrame#navigationPanel {{
            background-color: {PALETTE.surface_primary};
            border-right: 1px solid {PALETTE.border};
            border-top-right-radius: 18px;
            border-bottom-right-radius: 18px;
            box-shadow: 2px 0 8px rgba(15, 23, 42, 0.08);
        }}

        QLabel#pageTitle {{
            color: {PALETTE.text_primary};
        }}

        QPushButton {{
            min-height: 40px;
            background-color: transparent;
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 12px;
            padding: 10px 16px;
            color: {PALETTE.text_primary};
        }}

        QPushButton:hover {{
            color: {PALETTE.highlight_soft};
            background-color: rgba(37, 99, 235, 0.12);
        }}

        QPushButton:pressed {{
            background-color: rgba(37, 99, 235, 0.2);
        }}

        QPushButton[secondary='true'] {{
            background-color: #f8fbff;
        }}

        QPushButton[accent='true'] {{
            background-color: {PALETTE.highlight};
            border-color: {PALETTE.highlight};
            color: #ffffff;
            font-weight: 600;
        }}

        QPushButton#helpButton {{
            border-radius: 18px;
            padding: 8px 16px;
            background-color: rgba(37, 99, 235, 0.12);
            border: 1px solid rgba(37, 99, 235, 0.35);
            color: {PALETTE.highlight};
        }}

        QPushButton#helpButton:hover {{
            background-color: rgba(37, 99, 235, 0.25);
        }}

        QLineEdit, QComboBox, QPlainTextEdit, QTextEdit, QSpinBox,
        QDoubleSpinBox, QDateEdit {{
            border: 1px solid {PALETTE.border};
            border-radius: 10px;
            padding: 8px 12px;
            background-color: {PALETTE.surface_primary};
            selection-background-color: {PALETTE.highlight};
            selection-color: #ffffff;
        }}

        QTreeView, QTableView, QTableWidget {{
            background-color: {PALETTE.surface_primary};
            alternate-background-color: {PALETTE.surface_secondary};
            gridline-color: rgba(99, 112, 133, 0.18);
            selection-background-color: rgba(37, 99, 235, 0.15);
            selection-color: {PALETTE.text_primary};
            border: 1px solid {PALETTE.border};
            border-radius: 10px;
        }}

        QHeaderView::section {{
            background-color: {PALETTE.surface_secondary};
            padding: 6px;
            border: none;
            color: {PALETTE.text_secondary};
        }}

        QScrollArea {{
            background-color: transparent;
        }}

        QScrollBar:vertical, QScrollBar:horizontal {{
            background: transparent;
            border: none;
            margin: 6px;
            border-radius: 6px;
        }}

        QScrollBar::handle {{
            background-color: rgba(148, 163, 184, 0.35);
            border-radius: 6px;
        }}

        QCalendarWidget QWidget {{
            alternate-background-color: rgba(37, 99, 235, 0.08);
        }}

        QFrame[role='card'] {{
            background-color: {PALETTE.card_background};
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.22);
            padding: 18px;
        }}

        QLabel[role='metricTitle'] {{
            color: {PALETTE.text_secondary};
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        QLabel[role='metricValue'] {{
            font-size: 32px;
            font-weight: 700;
            color: {PALETTE.text_primary};
        }}

        QLabel#statusHint {{
            color: {PALETTE.text_secondary};
            background-color: rgba(100, 116, 139, 0.12);
            padding: 10px 14px;
            border-radius: 12px;
        }}

        QStatusBar {{
            background: {PALETTE.surface_primary};
            color: {PALETTE.text_secondary};
            border-top: 1px solid {PALETTE.border};
        }}

        QStatusBar QLabel {{
            color: {PALETTE.text_secondary};
        }}
    """
