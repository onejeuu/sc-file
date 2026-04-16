from enum import StrEnum

from PySide6.QtGui import QColor


class Colors(StrEnum):
    ACCENT = "#ffd666"
    CARD = "#2b2b2b"
    BACKGROUND = "#1a1a1a"
    TEXT = "#abb2bf"
    WARNING = "#e2a03f"

    @property
    def darker(self):
        return QColor(self).darker(120).name()

    @property
    def dark(self):
        return QColor(self).darker(150).name()

    @property
    def lighter(self):
        return QColor(self).lighter(120).name()

    @property
    def light(self):
        return QColor(self).lighter(150).name()


class Styles:
    WINDOW = f"""
        QMainWindow, QDialog, QWidget {{ background: {Colors.BACKGROUND};  color: {Colors.TEXT}; font-family: "Segoe UI", sans-serif; }}
        QLabel {{ background: transparent; color: {Colors.TEXT}; }}
    """

    CHECKBOX = f"""
        QCheckBox {{ color: {Colors.TEXT}; spacing: 8px; }}
        QCheckBox:disabled {{ color: {Colors.TEXT.dark}; }}
        QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {Colors.CARD.lighter}; background: {Colors.CARD}; }}
        QCheckBox::indicator:unchecked:hover {{ border: 1px solid {Colors.ACCENT}; }}
        QCheckBox::indicator:disabled {{ background: transparent; border: 1px solid {Colors.CARD.darker}; }}
        QCheckBox::indicator:checked {{ background: {Colors.ACCENT}; border: 1px solid {Colors.ACCENT}; }}
        QCheckBox::indicator:checked:hover {{ background: {Colors.ACCENT.darker}; border: 1px solid {Colors.ACCENT.darker}; }}
        QCheckBox::indicator:checked:disabled {{ background: {Colors.CARD.light}; border: 1px solid {Colors.CARD.light}; }}
    """

    RADIO = f"""
        QRadioButton {{ color: {Colors.TEXT}; spacing: 8px; }}
        QRadioButton:disabled {{ color: {Colors.TEXT.dark}; }}
        QRadioButton::indicator {{ width: 14px; height: 14px; border: 1px solid {Colors.CARD.lighter}; background: {Colors.CARD}; border-radius: 7px; }}
        QRadioButton::indicator:unchecked:hover {{ border: 1px solid {Colors.ACCENT}; }}
        QRadioButton::indicator:disabled {{ background: transparent; border: 1px solid {Colors.CARD.darker}; }}
        QRadioButton::indicator:checked {{ background: {Colors.ACCENT}; border: 1px solid {Colors.ACCENT}; }}
        QRadioButton::indicator:checked:hover {{ background: {Colors.ACCENT.darker}; border: 1px solid {Colors.ACCENT.darker}; }}
        QRadioButton::indicator:checked:disabled {{ background: {Colors.CARD.light}; border: 1px solid {Colors.CARD.light}; }}
    """

    LIST = f"""
        QListWidget {{ background: {Colors.CARD}; color: {Colors.TEXT}; border: 1px solid {Colors.CARD.lighter}; outline: none; font-size: 12px; }}
        QListWidget::item {{ padding: 3px 5px; }}
        QListWidget::item:selected {{ background: {Colors.CARD.lighter}; color: #ffffff; }}
        QListWidget::item:hover, QListWidget::item:selected:hover {{ background: {Colors.CARD.light}; }}
    """

    COMBO = f"""
        QComboBox {{ background: {Colors.CARD}; border: 1px solid {Colors.CARD.lighter}; padding: 2px 10px; }}
        QComboBox:hover {{ border: 1px solid {Colors.ACCENT}; }}
        QComboBox::drop-down {{ border: none; background: transparent; }}
        QComboBox QAbstractItemView {{ background: {Colors.CARD}; color: {Colors.TEXT}; border: 1px solid {Colors.CARD.lighter}; outline: none; }}
        QComboBox QAbstractItemView::item {{ min-height: 20px; padding-left: 10px; border: none; }}
        QComboBox QAbstractItemView::item:selected {{ background: {Colors.CARD.lighter}; color: {Colors.ACCENT}; }}
        QComboBox QAbstractItemView::item:hover {{ background: {Colors.CARD.light}; }}
    """

    CONVERT = f"""
        QPushButton {{ background: {Colors.ACCENT}; color: black; font-weight: bold; font-size: 15px; border: none; }}
        QPushButton:hover {{ background: {Colors.ACCENT.lighter}; }}
        QPushButton:disabled {{ background: {Colors.CARD.light}; color: {Colors.TEXT.dark}; }}
    """

    INPUT = f"""
        QLineEdit {{ background: {Colors.BACKGROUND}; color: {Colors.TEXT}; border: 1px solid {Colors.CARD.lighter}; padding: 4px; }}
        QLineEdit:disabled {{ background: {Colors.CARD.darker}; color: {Colors.TEXT.darker}; border: 1px solid {Colors.CARD}; }}
    """

    TAB = f"""
        QTabBar::tab {{ background: {Colors.BACKGROUND}; color: {Colors.TEXT}; padding: 10px 20px; min-width: 120px; border: none; font-weight: bold; }}
        QTabBar::tab:selected {{ background: {Colors.CARD}; color: white; border-bottom: 2px solid {Colors.ACCENT}; }}
        QTabBar::tab:hover {{ background: {Colors.CARD.darker}; }}
    """

    TITLE = "font-weight: bold; font-size: 16px;"
    LABEL = "font-weight: bold; font-size: 14px;"

    HINT = f"color: {Colors.TEXT.dark}; font-size: 10px; margin-left: 24px;"
    WARNING = f"font-weight: medium; color: {Colors.WARNING}; font-size: 12px; line-height: 120%;"
