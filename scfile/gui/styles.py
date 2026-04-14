class Colors:
    ACCENT = "#FFD666"
    CARD = "#2b2b2b"
    BACKGROUND = "#1a1a1a"
    TEXT = "#abb2bf"


class Styles:
    WINDOW = f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {Colors.BACKGROUND}; 
            color: {Colors.TEXT};
            font-family: "Segoe UI", sans-serif;
        }}
        QLabel {{
            color: {Colors.TEXT};
            background: transparent;
        }}
    """

    CHECKBOX = f"""
        QCheckBox {{ color: {Colors.TEXT}; spacing: 8px; }}
        QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid #555; background: {Colors.CARD}; }}
        QCheckBox::indicator:checked {{ background: {Colors.ACCENT}; border: 1px solid {Colors.ACCENT}; }}
        QCheckBox::indicator:unchecked:hover {{ border: 1px solid {Colors.ACCENT}; }}
        QCheckBox:disabled {{ color: #555; }}
        QCheckBox::indicator:disabled {{ background: {Colors.BACKGROUND}; border: 1px solid #333; }}
    """

    RADIO = f"""
        QRadioButton {{ color: {Colors.TEXT}; spacing: 8px; font-size: 11px; }}
        QRadioButton::indicator {{ width: 14px; height: 14px; border-radius: 7px; border: 1px solid #555; background: {Colors.CARD}; }}
        QRadioButton::indicator:checked {{ background: {Colors.ACCENT}; border: 1px solid {Colors.ACCENT}; }}
        QRadioButton:disabled {{ color: #555; }}
    """

    LIST = f"""
        QListWidget {{
            background: {Colors.CARD};
            color: {Colors.TEXT};
            border: 1px solid #555;
            outline: none;
            font-size: 12px;
        }}
        QListWidget::item {{ padding: 3px 5px; }}
        QListWidget::item:selected {{ background: #3e4451; color: #ffffff; }}
    """

    COMBO = f"""
        QComboBox {{
            background: {Colors.CARD};
            border: 1px solid #555;
            padding: 2px 10px;
        }}
        QComboBox::drop-down {{
            border: none;
            background: transparent;
        }}
        QComboBox QAbstractItemView {{
            background: {Colors.CARD};
            color: {Colors.TEXT};
            border: 1px solid #555;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            min-height: 20px;
            padding-left: 10px;
            border: none;
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: #3d4455;
            color: white;
        }}
    """

    CONVERT = f"""
        QPushButton {{ background: {Colors.ACCENT}; color: black; font-weight: bold; font-size: 15px; border: none; }}
        QPushButton:hover {{ background: #ffe08a; }}
        QPushButton:disabled {{ background: #444; color: #888; }}
    """

    INPUT = f"""
        QLineEdit {{
            background: {Colors.BACKGROUND}; color: {Colors.TEXT};
            border: 1px solid #555; padding: 4px;
        }}
        QLineEdit:disabled {{ background: #222; color: #555; border: 1px solid #333; }}
    """

    HINT = """color: #5c6370; font-size: 10px; margin-left: 24px;"""
