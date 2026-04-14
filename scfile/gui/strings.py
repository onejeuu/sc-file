import locale
from typing import Literal, TypeAlias


Lang: TypeAlias = Literal["EN"] | Literal["RU"]


def _get_lang() -> Lang:
    lang = str(locale.getdefaultlocale()[0] or "")
    return "RU" if lang.startswith("ru") else "EN"


class Strings:
    LANG: Lang = _get_lang()

    DATA: dict[str, dict[Lang, str]] = {
        "action_remove": {"EN": "Remove from list", "RU": "Удалить из списка"},
        "drop_hint": {
            "EN": "Add files/folders with buttons above\nor drag & drop them here",
            "RU": "Добавьте файлы/папки кнопками выше\nили перетащите их сюда (drag & drop)",
        },
        "label_sources": {"EN": "Sources", "RU": "Источники"},
        "label_settings": {"EN": "Settings", "RU": "Настройки"},
        "label_output_path": {"EN": "Output Path", "RU": "Путь сохранения"},
        "btn_add_files": {"EN": "+ Files", "RU": "+ Файлы"},
        "btn_add_folder": {"EN": "+ Folder", "RU": "+ Папка"},
        "btn_convert": {"EN": "CONVERT", "RU": "КОНВЕРТИРОВАТЬ"},
        "opt_output_default": {"EN": "In the same folder as original", "RU": "В папку с оригинальным файлом"},
        "opt_output_flat": {"EN": "Flat folder", "RU": "В одну папку"},
        "opt_output_tree": {"EN": "Keep subfolder structure", "RU": "Сохранять структуру подпапок"},
        "placeholder_path": {"EN": "Specify path...", "RU": "Укажите путь..."},
        "cb_unique_names": {"EN": "Create copies on name collision", "RU": "Создавать копии при совпадении имен"},
        "hint_unique_names": {
            "EN": "Add a sequence number to the filename instead of overwriting it",
            "RU": "Добавлять порядковый номер к названию файла вместо его перезаписи",
        },
        "tooltip_no_sources": {"EN": "Add sources to convert", "RU": "Добавьте источники для конвертации"},
        "dialog_files": {"EN": "Files", "RU": "Файлы"},
        "dialog_folder": {"EN": "Folder", "RU": "Папка"},
        "dialog_output": {"EN": "Output Directory", "RU": "Папка результатов"},
        "feat_skeleton": {"EN": "Skeleton", "RU": "Скелет"},
        "feat_animation": {"EN": "Animation", "RU": "Анимация"},
        "fmt_models": {"EN": "Models", "RU": "Модели"},
        "fmt_textures": {"EN": "Textures", "RU": "Текстуры"},
        "fmt_images": {"EN": "Images", "RU": "Изображения"},
        "fmt_texarr": {"EN": "Texture Array", "RU": "Массив текстур"},
        "fmt_nbt": {"EN": "NBT Data", "RU": "NBT Данные"},
    }

    @classmethod
    def get(cls, key: str) -> str:
        return cls.DATA.get(key, {}).get(cls.LANG, key)
