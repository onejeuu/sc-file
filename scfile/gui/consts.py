from typing import NamedTuple

from scfile.consts import NBT_FILENAMES


FEATURE_ICONS = {
    "skeleton": "🦴",
    "animation": "🌀",
}


class FileType(NamedTuple):
    id: str
    label: str
    suffixes: list[str]
    features: dict[str, str] = {}


FILE_TYPES = [
    FileType(
        "models",
        "🧊 Модели",
        [".mcsa", ".mcsb", ".mcvd"],
        features={"skeleton": "🦴 Скелет", "animation": "🌀 Анимация"},
    ),
    FileType("textures", "🧱 Текстуры", [".ol"]),
    FileType("images", "🖼 Изображения", [".mic"]),
    FileType("texarr", "🗃️ Массив текстур", [".texarr"]),
    FileType("nbt", "⚙️ NBT Данные", list(sorted(NBT_FILENAMES))),
]

FORMATS = [
    {"name": "OBJ", "skeleton": False, "animation": False},
    {"name": "GLB", "skeleton": True, "animation": True},
    {"name": "DAE", "skeleton": True, "animation": False},
    {"name": "MS3D", "skeleton": True, "animation": False},
]


class Colors:
    ACCENT = "#FFD666"
    CARD = "#2b2b2b"
    BACKGROUND = "#1a1a1a"
    TEXT = "#abb2bf"
    DIMMED = "#5c6370"


class Styles:
    CHECKBOX = f"""
        QCheckBox {{ color: {Colors.TEXT}; spacing: 8px; }}
        QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid #555; background: {Colors.CARD}; }}
        QCheckBox::indicator:checked {{ background: {Colors.ACCENT}; border: 1px solid {Colors.ACCENT}; }}
        QCheckBox::indicator:unchecked:hover {{ border: 1px solid {Colors.ACCENT}; }}
        QCheckBox:disabled {{ color: #555; }}
        QCheckBox::indicator:disabled {{ background: #1a1a1a; border: 1px solid #333; }}
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

    CONVERT = f"""
        QPushButton {{ background: {Colors.ACCENT}; color: black; font-weight: bold; font-size: 15px; border: none; }}
        QPushButton:hover {{ background: #ffe08a; }}
        QPushButton:disabled {{ background: #444; color: #888; }}
    """

    INPUT = f"""
        QLineEdit {{
            background: {Colors.CARD}; color: {Colors.DIMMED};
            border: 1px solid #555; padding: 4px;
        }}
        QLineEdit:disabled {{ background: #222; color: #555; border: 1px solid #333; }}
    """
