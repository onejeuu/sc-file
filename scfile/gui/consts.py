from dataclasses import dataclass, field

from scfile.consts import NBT_FILENAMES


@dataclass
class Feature:
    id: str
    label: str
    icon: str

    @property
    def title(self) -> str:
        return f"{self.icon} {self.label}"


class F:
    SKELETON = Feature("skeleton", "Скелет", "🦴")
    ANIMATION = Feature("animation", "Анимация", "🌀")


@dataclass
class FileType:
    id: str
    label: str
    suffixes: list[str]
    features: list[Feature] = field(default_factory=list)

    @property
    def feature_map(self) -> dict[str, str]:
        return {f.id: f.title for f in self.features}


FILE_TYPES: list[FileType] = [
    FileType("models", "🧊 Модели", suffixes=[".mcsa", ".mcsb", ".mcvd"], features=[F.SKELETON, F.ANIMATION]),
    FileType("textures", "🧱 Текстуры", suffixes=[".ol"]),
    FileType("images", "🖼 Изображения", suffixes=[".mic"]),
    FileType("texarr", "🗃️ Массив текстур", suffixes=[".texarr"]),
    FileType("nbt", "⚙️ NBT Данные", suffixes=list(sorted(NBT_FILENAMES))),
]


@dataclass
class ModelFormat:
    name: str
    features: list[Feature] = field(default_factory=list)

    def __str__(self) -> str:
        icons = " ".join(f.icon for f in self.features)
        return f"{self.name} {icons}".strip()


MODEL_FORMATS = [
    ModelFormat("OBJ"),
    ModelFormat("GLB", features=[F.SKELETON, F.ANIMATION]),
    ModelFormat("DAE", features=[F.SKELETON]),
    ModelFormat("MS3D", features=[F.SKELETON]),
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
