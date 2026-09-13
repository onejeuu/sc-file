from enum import Enum

from PySide6.QtGui import QColor

from scfile.app import files
from scfile.app.consts import ACCENT_COLOR


CHECK_ICON = files.resource("assets/ui.check.png").as_posix()
CHEVRON_DOWN_ICON = files.resource("assets/ui.chevron.down.png").as_posix()
CHEVRON_UP_ICON = files.resource("assets/ui.chevron.up.png").as_posix()
MAX_FORM_WIDTH = 960


class Colors(Enum):
    ACCENT = QColor(ACCENT_COLOR)
    ACCENT_HOVER = QColor("#FFE08A")
    ACCENT_PRESSED = QColor("#E7BF59")
    ACCENT_FOREGROUND = QColor("#181307")

    CANVAS = QColor("#0F1115")
    SIDEBAR = QColor("#14171C")
    SURFACE = QColor("#191D23")
    SURFACE_RAISED = QColor("#1D2229")
    SURFACE_SUNKEN = QColor("#12161B")
    CONTROL = QColor("#1E232A")
    CONTROL_HOVER = QColor("#262C34")
    CONTROL_PRESSED = QColor("#303741")
    CONTROL_DISABLED = QColor("#171B20")

    BORDER = QColor("#2B313A")
    BORDER_STRONG = QColor("#3A424E")

    INDICATOR = QColor("#737C89")
    INDICATOR_DISABLED = QColor("#5E6672")

    TEXT = QColor("#F3F4F6")
    TEXT_SECONDARY = QColor("#A6AEBB")
    TEXT_MUTED = QColor("#8993A1")
    TEXT_DISABLED = QColor("#5E6672")

    INFO = QColor("#78B7FF")
    SUCCESS = QColor("#63C98E")
    WARNING = QColor("#F2B84B")
    ERROR = QColor("#F07178")

    def alpha(self, opacity: float) -> str:
        return f"rgba({self.value.red()}, {self.value.green()}, {self.value.blue()}, {opacity})"

    def __str__(self) -> str:
        return self.value.name()


class Styles:
    WINDOW = f"""
        QMainWindow, QDialog {{
            color: {Colors.TEXT};
            font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
            font-size: 13px;
        }}
        QWidget {{
            color: {Colors.TEXT};
            font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
        }}
        QMainWindow {{ background: transparent; }}
        QDialog {{ background: {Colors.CANVAS}; }}
        QWidget#appRoot {{ background: {Colors.CANVAS}; border: 1px solid {Colors.BORDER}; border-radius: 8px; }}
        QWidget#appRoot[maximized="true"] {{ border-radius: 0px; }}
        QWidget#windowBody, QWidget#mainContent, QStackedWidget {{ background: {Colors.CANVAS}; }}
        QLabel {{ background: transparent; color: {Colors.TEXT}; }}
    """

    CHECKBOX = f"""
        QCheckBox {{ color: {Colors.TEXT}; spacing: 8px; min-height: 20px; outline: none; }}
        QCheckBox:hover {{ color: {Colors.TEXT}; }}
        QCheckBox:disabled {{ color: {Colors.TEXT_DISABLED}; }}
        QCheckBox::indicator {{
            width: 16px; height: 16px;
            border: 1px solid {Colors.BORDER};
            background: {Colors.CONTROL};
            border-radius: 4px;
        }}
        QCheckBox::indicator:unchecked:hover,
        QCheckBox[hovered="true"]::indicator:unchecked:enabled {{ border-color: {Colors.ACCENT}; }}
        QCheckBox::indicator:disabled {{ background: {Colors.CONTROL_DISABLED}; border-color: {Colors.BORDER}; }}
        QCheckBox::indicator:checked {{
            image: url("{CHECK_ICON}");
            background: {Colors.ACCENT};
            border-color: {Colors.ACCENT};
        }}
        QCheckBox::indicator:checked:hover,
        QCheckBox[hovered="true"]::indicator:checked:enabled {{ background: {Colors.ACCENT_HOVER}; border-color: {Colors.ACCENT_HOVER}; }}
        QCheckBox::indicator:checked:disabled {{ background: {Colors.INDICATOR_DISABLED}; border-color: {Colors.INDICATOR_DISABLED}; }}
    """

    RADIO = f"""
        QRadioButton {{ color: {Colors.TEXT}; spacing: 8px; min-height: 20px; outline: none; }}
        QRadioButton:disabled {{ color: {Colors.TEXT_DISABLED}; }}
        QRadioButton::indicator {{
            width: 16px; height: 16px;
            border: 1px solid {Colors.INDICATOR};
            background: {Colors.CONTROL};
            border-radius: 8px;
        }}
        QRadioButton::indicator:unchecked:hover {{ border-color: {Colors.ACCENT}; }}
        QRadioButton::indicator:disabled {{ background: {Colors.CONTROL_DISABLED}; border-color: {Colors.BORDER}; }}
        QRadioButton::indicator:checked {{ background: {Colors.ACCENT}; border-color: {Colors.ACCENT}; }}
        QRadioButton::indicator:checked:hover {{ background: {Colors.ACCENT_HOVER}; border-color: {Colors.ACCENT_HOVER}; }}
        QRadioButton::indicator:checked:disabled {{ background: {Colors.INDICATOR_DISABLED}; border-color: {Colors.INDICATOR_DISABLED}; }}
    """

    SOURCES_EMPTY = """
        QListWidget {
            background: transparent;
            border: none;
            outline: none;
        }
    """

    SOURCES_LIST = f"""
        QListWidget {{
            background: {Colors.SURFACE};
            color: {Colors.TEXT_SECONDARY};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            outline: none;
            selection-background-color: {Colors.CONTROL_HOVER};
            selection-color: {Colors.TEXT};
            font-size: 12px;
        }}
        QListWidget::item {{
            color: {Colors.TEXT_SECONDARY};
            min-height: 34px;
            padding: 0px 10px;
            border-bottom: 1px solid {Colors.BORDER};
        }}
        QListWidget::item:last {{ border-bottom: none; }}
        QListWidget::item:hover {{ background: {Colors.CONTROL}; color: {Colors.TEXT}; }}
        QListWidget::item:selected,
        QListWidget::item:selected:active,
        QListWidget::item:selected:!active {{
            background: {Colors.CONTROL_HOVER};
            color: {Colors.TEXT};
        }}
    """

    MENU = f"""
        QMenu {{
            background: {Colors.SURFACE_RAISED};
            color: {Colors.TEXT};
            border: 1px solid {Colors.BORDER_STRONG};
            border-radius: 6px;
            padding: 4px 0px;
        }}
        QMenu::item {{
            background: transparent;
            color: {Colors.TEXT_SECONDARY};
            border-radius: 4px;
            padding: 7px 12px;
            margin: 0px 4px;
        }}
        QMenu::item:selected {{ background: {Colors.CONTROL_HOVER}; color: {Colors.TEXT}; }}
        QMenu::item:disabled {{ color: {Colors.TEXT_DISABLED}; }}
        QMenu::separator {{ height: 1px; background: {Colors.BORDER}; margin: 4px 8px; }}
    """

    COUNT_BADGE = f"""
        QLabel#sourceCount {{
            min-width: 22px;
            min-height: 20px;
            max-height: 20px;
            padding: 0px;
            background: {Colors.ACCENT};
            border: none;
            border-radius: 10px;
            color: {Colors.ACCENT_FOREGROUND};
            font-size: 11px;
            font-weight: 700;
        }}
    """

    FORMAT_CARD = f"""
        QWidget#formatCard {{
            background: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
        }}
        QWidget#formatCard[hovered="true"] {{
            background: {Colors.SURFACE};
            border-color: {Colors.ACCENT};
        }}
        QWidget#formatCard[checked="false"] {{
            background: {Colors.SURFACE_SUNKEN};
            border-color: {Colors.BORDER};
        }}
        QWidget#formatCard[checked="false"][hovered="true"] {{
            background: {Colors.SURFACE_SUNKEN};
            border-color: {Colors.ACCENT};
        }}
        QWidget#formatCard:disabled {{
            background: {Colors.CONTROL_DISABLED};
            border-color: {Colors.BORDER};
        }}
        QWidget#formatCard QLabel#formatCardTitle {{
            color: {Colors.TEXT};
            font-size: 14px;
            font-weight: 600;
        }}
        QWidget#formatCard[checked="false"] QLabel#formatCardTitle,
        QWidget#formatCard:disabled QLabel#formatCardTitle {{
            color: {Colors.TEXT_SECONDARY};
        }}
        QWidget#formatCard QLabel#formatCardHint {{
            color: {Colors.TEXT_MUTED};
            font-size: 12px;
        }}
        QWidget#formatCard:disabled QLabel#formatCardHint {{
            color: {Colors.TEXT_DISABLED};
        }}
        QWidget#formatCard QLabel#formatCardTarget {{
            color: {Colors.TEXT_SECONDARY};
            font-size: 14px;
            font-weight: 600;
        }}
        QWidget#formatCard:disabled QLabel#formatCardTarget {{
            color: {Colors.TEXT_DISABLED};
        }}
    """

    CARD = f"""
        QWidget#card {{
            background: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
        }}
    """

    CARD_TITLE = f"font-size: 14px; font-weight: 600; color: {Colors.TEXT};"

    CALLOUT = f"""
        QWidget#callout {{
            background: {Colors.INFO.alpha(0.04)};
            border: 1px solid {Colors.INFO.alpha(0.24)};
            border-radius: 8px;
        }}
    """

    BADGE_WARNING = f"""
        QLabel {{
            background: {Colors.WARNING.alpha(0.10)};
            color: {Colors.WARNING};
            border: 1px solid {Colors.WARNING};
            border-radius: 7px;
            padding: 1px 6px;
            font-size: 10px;
            font-weight: 600;
        }}
    """

    COMBO = f"""
        QComboBox {{
            background: {Colors.CONTROL};
            color: {Colors.TEXT};
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            padding: 0px 10px;
            min-height: 30px;
            outline: none;
            font-weight: 600;
        }}
        QComboBox:hover {{ border-color: {Colors.BORDER_STRONG}; background: {Colors.CONTROL_HOVER}; }}
        QComboBox:disabled {{ background: {Colors.CONTROL_DISABLED}; color: {Colors.TEXT_DISABLED}; border-color: {Colors.BORDER}; }}
        QComboBox::drop-down {{ border: none; background: transparent; width: 28px; }}
        QComboBox::down-arrow {{
            image: url("{CHEVRON_DOWN_ICON}");
            width: 16px;
            height: 16px;
        }}
    """

    COMBO_POPUP = f"""
        QAbstractItemView {{
            background: {Colors.SURFACE_RAISED};
            color: {Colors.TEXT};
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            outline: none;
            padding: 4px 0px;
            font-weight: 400;
        }}
        QAbstractItemView::item {{
            padding-left: 10px;
            padding-right: 10px;
            border: none;
            border-radius: 4px;
            margin: 0px 4px;
        }}
        QAbstractItemView::item:selected {{ background: {Colors.CONTROL_HOVER}; color: {Colors.TEXT}; }}
        QAbstractItemView::item:hover {{ background: {Colors.CONTROL}; color: {Colors.TEXT}; }}
        QAbstractItemView::item:selected:hover {{ background: {Colors.CONTROL_PRESSED}; }}
    """

    COMBO_CONTAINER = """
        QWidget#comboPopup { background: transparent; border: none; }
    """

    TITLE_BAR = f"""
        QWidget#titleBar {{ background: {Colors.CANVAS}; border: none; }}
        QWidget#titleBrand {{ background: {Colors.SIDEBAR}; border: none; border-right: 1px solid {Colors.BORDER}; }}
        QLabel#windowIcon, QLabel#windowTitle {{ background: transparent; border: none; }}
        QLabel#windowTitle {{ color: {Colors.TEXT}; font-size: 12px; font-weight: 600; }}
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: 0px;
            color: {Colors.TEXT_SECONDARY};
            padding: 0px;
            outline: none;
        }}
        QPushButton:hover {{ background: {Colors.CONTROL_HOVER}; color: {Colors.TEXT}; }}
        QPushButton:pressed {{ background: {Colors.CONTROL_PRESSED}; }}
        QPushButton#closeButton:hover {{ background: #C42B1C; color: white; }}
        QPushButton#closeButton:pressed {{ background: #A51D13; color: white; }}
    """

    BUTTON = f"""
        QPushButton {{
            background: {Colors.CONTROL};
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            color: {Colors.TEXT};
            min-height: 30px;
            padding: 0px 10px;
            outline: none;
        }}
        QPushButton:hover {{ background: {Colors.CONTROL_HOVER}; border-color: {Colors.BORDER_STRONG}; }}
        QPushButton:pressed {{ background: {Colors.CONTROL_PRESSED}; }}
        QPushButton:disabled {{ background: {Colors.CONTROL_DISABLED}; color: {Colors.TEXT_DISABLED}; border-color: {Colors.BORDER}; }}
    """

    BUTTON_UTILITY = f"""
        QPushButton {{
            background: {Colors.SURFACE};
            border: 1px solid {Colors.BORDER};
            border-radius: 5px;
            color: {Colors.TEXT_SECONDARY};
            min-height: 24px;
            max-height: 24px;
            padding: 0px 9px;
            font-size: 12px;
            font-weight: 600;
            outline: none;
        }}
        QPushButton:hover {{ background: {Colors.CONTROL}; border-color: {Colors.BORDER_STRONG}; color: {Colors.TEXT}; }}
        QPushButton:pressed {{ background: {Colors.CONTROL_PRESSED}; }}
        QPushButton:disabled {{ background: transparent; color: {Colors.TEXT_DISABLED}; border-color: {Colors.BORDER}; }}
    """

    BUTTON_ACCENT = f"""
        QPushButton {{
            background: {Colors.ACCENT};
            color: {Colors.ACCENT_FOREGROUND};
            font-weight: 700;
            font-size: 14px;
            border: 1px solid {Colors.ACCENT};
            border-radius: 8px;
            min-height: 42px;
            outline: none;
        }}
        QPushButton:hover {{ background: {Colors.ACCENT_HOVER}; border-color: {Colors.ACCENT_HOVER}; }}
        QPushButton:pressed {{ background: {Colors.ACCENT_PRESSED}; border-color: {Colors.ACCENT_PRESSED}; padding-top: 2px; }}
        QPushButton:disabled {{ background: {Colors.CONTROL_PRESSED}; color: {Colors.TEXT_DISABLED}; border-color: {Colors.CONTROL_PRESSED}; }}
    """

    INPUT = f"""
        QLineEdit {{
            placeholder-text-color: {Colors.TEXT_MUTED};
            background: {Colors.SURFACE_SUNKEN};
            color: {Colors.TEXT};
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            min-height: 30px;
            padding: 0px 8px;
            outline: none;
        }}
        QLineEdit:hover {{ border-color: {Colors.BORDER_STRONG}; }}
        QLineEdit[invalid="true"] {{ border-color: {Colors.ERROR}; }}
        QLineEdit:disabled {{ background: {Colors.CONTROL_DISABLED}; color: {Colors.TEXT_DISABLED}; border-color: {Colors.BORDER}; }}
        QLineEdit:read-only:enabled {{ color: {Colors.TEXT_SECONDARY}; }}
    """

    SLIDER = f"""
        QSlider::groove:horizontal {{ height: 4px; background: {Colors.BORDER}; border-radius: 2px; }}
        QSlider::sub-page:horizontal {{ background: {Colors.ACCENT}; border-radius: 2px; }}
        QSlider::handle:horizontal {{ width: 14px; margin: -5px 0px; background: {Colors.TEXT}; border-radius: 7px; }}
        QSlider::handle:horizontal:hover {{ background: {Colors.ACCENT}; }}
        QSlider::sub-page:horizontal:disabled {{ background: {Colors.BORDER_STRONG}; }}
        QSlider::handle:horizontal:disabled {{ background: {Colors.INDICATOR_DISABLED}; }}
    """

    SPIN = f"""
        QSpinBox {{
            background: {Colors.CONTROL};
            color: {Colors.TEXT};
            border: 1px solid {Colors.BORDER};
            border-radius: 6px;
            min-height: 30px;
            padding: 0px 22px 0px 8px;
            outline: none;
        }}
        QSpinBox:hover {{ border-color: {Colors.BORDER_STRONG}; background: {Colors.CONTROL_HOVER}; }}
        QSpinBox:disabled {{ background: {Colors.CONTROL_DISABLED}; color: {Colors.TEXT_DISABLED}; border-color: {Colors.BORDER}; }}
        QSpinBox::up-button, QSpinBox::down-button {{
            subcontrol-origin: border;
            width: 18px;
            background: transparent;
            border: none;
            border-left: 1px solid {Colors.BORDER};
        }}
        QSpinBox::up-button {{ subcontrol-position: top right; }}
        QSpinBox::down-button {{ subcontrol-position: bottom right; }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {Colors.CONTROL_PRESSED}; }}
        QSpinBox::up-arrow {{ image: url("{CHEVRON_UP_ICON}"); width: 10px; height: 10px; }}
        QSpinBox::down-arrow {{ image: url("{CHEVRON_DOWN_ICON}"); width: 10px; height: 10px; }}
    """

    UPDATE = f"""
        UpdatePopup {{ background: transparent; }}
        QWidget#updateSurface {{ background-color: {Colors.SURFACE_RAISED}; border: 1px solid {Colors.BORDER_STRONG}; border-radius: 8px; }}
        QLabel {{ background: transparent; }}
    """

    SIDEBAR = f"""
        QWidget#sidebar {{ background: {Colors.SIDEBAR}; border-right: 1px solid {Colors.BORDER}; }}
    """

    FOOTER = f"""
        QWidget#footer {{ background: {Colors.CANVAS}; border-top: 1px solid {Colors.BORDER}; }}
    """

    SIDEBAR_ITEM = f"""
        QPushButton {{
            background: transparent;
            border: none;
            border-left: 3px solid transparent;
            padding: 0px;
            min-height: 40px;
            max-height: 40px;
            outline: none;
        }}
        QPushButton:hover {{ background: {Colors.SURFACE}; }}
        QPushButton:checked {{ background: {Colors.ACCENT.alpha(0.08)}; border-left-color: {Colors.ACCENT}; }}
        QPushButton:checked:hover {{ background: {Colors.ACCENT.alpha(0.12)}; }}
    """

    VERSION_BADGE = f"""
        QWidget#versionBadge {{
            background-color: {Colors.CONTROL};
            border: none;
            border-radius: 11px;
        }}
        QWidget#versionBadge QLabel {{
            background: transparent;
            border: none;
            color: {Colors.TEXT_SECONDARY};
            font-size: 11px;
            font-weight: 600;
        }}
    """
    VERSION_BADGE_HOVER = f"""
        QWidget#versionBadge {{
            background-color: {Colors.ACCENT.alpha(0.12)};
            border: none;
            border-radius: 11px;
        }}
        QWidget#versionBadge QLabel {{
            background: transparent;
            border: none;
            color: {Colors.ACCENT};
            font-size: 11px;
            font-weight: 600;
        }}
    """

    TOGGLE_STATES = f"""
        QPushButton:checked {{ background: {Colors.ACCENT}; border-color: {Colors.ACCENT}; color: {Colors.ACCENT_FOREGROUND}; font-weight: 700; }}
        QPushButton:checked:hover {{ background: {Colors.ACCENT_HOVER}; border-color: {Colors.ACCENT_HOVER}; }}
        QPushButton:hover:!checked {{ background: {Colors.CONTROL}; color: {Colors.TEXT}; }}
    """

    TOGGLE_GROUP = f"""
        QWidget#toggleGroup {{ background: {Colors.SURFACE_SUNKEN}; border: 1px solid {Colors.BORDER}; border-radius: 6px; }}
    """

    TOGGLE_ITEM = (
        f"""
        QPushButton {{
            background: transparent;
            color: {Colors.TEXT_SECONDARY};
            border: 1px solid transparent;
            border-radius: 4px;
            min-height: 28px;
            padding: 0px 8px;
            font-size: 12px;
            outline: none;
        }}
    """
        + TOGGLE_STATES
    )

    TABS = f"""
        QTabBar::tab {{ color: {Colors.TEXT_MUTED}; background: transparent; border: none; border-bottom: 2px solid transparent; padding: 8px 14px; }}
        QTabBar::tab:selected {{ color: {Colors.ACCENT}; border-bottom-color: {Colors.ACCENT}; font-weight: 600; }}
        QTabBar::tab:hover:!selected {{ color: {Colors.TEXT_SECONDARY}; }}
    """

    LINK = f"""background-color: transparent; color: {Colors.TEXT_MUTED}; font-size: 12px;"""
    LINK_HOVER = f"""background-color: transparent; color: {Colors.ACCENT}; font-size: 12px;"""

    TITLE = f"font-weight: 700; color: {Colors.TEXT}; font-size: 16px;"
    LABEL = f"font-weight: 600; color: {Colors.TEXT}; font-size: 13px;"

    SECONDARY = f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
    HINT = f"color: {Colors.TEXT_MUTED}; font-size: 12px;"
    OPTION_CHECKBOX = (
        CHECKBOX
        + f"""
        QCheckBox {{ color: {Colors.TEXT_SECONDARY}; }}
        QCheckBox:hover {{ color: {Colors.TEXT}; }}
        QCheckBox:disabled {{ color: {Colors.TEXT_DISABLED}; }}
    """
    )
    ERROR = f"color: {Colors.ERROR}; font-size: 12px;"

    WARNING = f"font-weight: 500; color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
