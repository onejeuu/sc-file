import locale
from typing import Literal, TypeAlias


Lang: TypeAlias = Literal["EN"] | Literal["RU"]


def _get_lang() -> Lang:
    lang = str(locale.getdefaultlocale()[0] or "")
    return "RU" if lang.startswith("ru") else "EN"


class Strings:
    LANG: Lang = _get_lang()

    DATA: dict[str, dict[Lang, str]] = {
        "tab_converter": {"EN": "Converter", "RU": "Конвертер файлов"},
        "tab_mapcache": {"EN": "Map Cache", "RU": "Кэш карты"},
        "tab_retarget": {"EN": "Retarget", "RU": "Ретаргет анимаций"},
        "action_remove": {"EN": "Remove from list", "RU": "Удалить из списка"},
        "drop_hint": {
            "EN": "Add files/folders with buttons above\nor drag & drop them here",
            "RU": "Добавьте файлы/папки кнопками выше\nили перетащите их сюда (drag & drop)",
        },
        "label_sources": {"EN": "Sources", "RU": "Источники"},
        "label_settings": {"EN": "Settings", "RU": "Настройки"},
        "label_output_path": {"EN": "Output Path", "RU": "Путь сохранения"},
        "label_mapcache_source": {"EN": "Stalcraft map cache folder", "RU": "Папка кэша карты сталкрафт"},
        "label_mapcache_output": {"EN": "Minecraft regions folder", "RU": "Папка регионов майнкрафт карты"},
        "btn_add_files": {"EN": "+ Files", "RU": "+ Файлы"},
        "btn_add_folder": {"EN": "+ Folder", "RU": "+ Папка"},
        "btn_convert": {"EN": "CONVERT", "RU": "КОНВЕРТИРОВАТЬ"},
        "btn_merge_regions": {"EN": "CONVERT", "RU": "КОНВЕРТИРОВАТЬ"},
        "opt_output_default": {"EN": "Same folder as original", "RU": "Рядом с оригинальным файлом"},
        "opt_output_flat": {"EN": "Single flat folder", "RU": "В одну плоскую папку"},
        "opt_output_tree": {"EN": "Keep subfolder structure", "RU": "Сохранять структуру подпапок"},
        "placeholder_path": {"EN": "Specify path...", "RU": "Укажите путь..."},
        "cb_unique_names": {"EN": "Create copies on name collision", "RU": "Создавать копии при совпадении имен"},
        "cb_raw_blocks": {"EN": "Raw blocks", "RU": "Raw blocks"},
        "cb_auto_resolve": {"EN": "Auto-resolve paths", "RU": "Автоматическое исправление путей"},
        "hint_unique_names": {
            "EN": "Add a sequence number to the filename instead of overwriting it",
            "RU": "Добавлять порядковый номер к названию файла вместо его перезаписи",
        },
        "hint_raw_blocks": {
            "EN": "Literal interpretation of block IDs instead of lookup table replacement",
            "RU": "Буквальная интерпретация айди блоков вместо замены по lookup таблице",
        },
        "hint_auto_resolve": {
            "EN": "Automatically complete the path to the data storage directory",
            "RU": "Автоматическое достраивание пути до директории с данными",
        },
        "tooltip_no_sources": {"EN": "Add sources to convert", "RU": "Добавьте источники для конвертации"},
        "tooltip_no_targets": {
            "EN": "No valid files found in sources",
            "RU": "В источниках не найдено подходящих файлов",
        },
        "tooltip_invalid_output": {
            "EN": "Specify a valid output directory",
            "RU": "Укажите корректный путь сохранения",
        },
        "tooltip_bad_mapcache_source": {
            "EN": "No .mdat files found in the specified directory",
            "RU": "В указанной папке не найдены файлы .mdat",
        },
        "warn_game_dir": {
            "EN": "Output path is within the game directory.",
            "RU": "Путь сохранения находится внутри директории игры.",
        },
        "warn_path_collision": {
            "EN": "Output directory is the same as one of the sources.",
            "RU": "Путь сохранения совпадает с одним из источников.",
        },
        "warn_not_minecraft_world": {
            "EN": "No Minecraft world data found at the specified path.",
            "RU": "По указанному пути не найдены данные мира Minecraft.",
        },
        "warn_regions_overwrite": {
            "EN": 'Regions in world "{world}" will be overwritten!',
            "RU": 'Регионы в мире "{world}" будут перезаписаны!',
        },
        "info_mdat_context": {
            "EN": "Format: Anvil 1343 (Minecraft 1.12.2+).\nExperimental decoder designed for basic geometry preview.\nFull environment replication or accurate block states are not planned.",
            "RU": "Формат: Anvil 1343 (Minecraft 1.12.2+).\nЭкспериментальный декодер для просмотра базовой геометрии.\nПолное воссоздание окружения и состояний блоков не планируется.",
        },
        "dialog_files": {"EN": "Files", "RU": "Файлы"},
        "dialog_folder": {"EN": "Folder", "RU": "Папка"},
        "dialog_output": {"EN": "Output Directory", "RU": "Папка результатов"},
        "dialog_mapcache_source": {"EN": "Stalcraft map cache", "RU": "Сталкрафт кэш карты"},
        "dialog_mapcache_output": {"EN": "Minecraft regions", "RU": "Майнкрафта регионы"},
        "feat_skeleton": {"EN": "Skeleton", "RU": "Скелет"},
        "feat_animation": {"EN": "Animation", "RU": "Анимация"},
        "feat_uv2": {"EN": "UVMap2", "RU": "UVMap2"},
        "fmt_models": {"EN": "Models", "RU": "Модели"},
        "fmt_textures": {"EN": "Textures", "RU": "Текстуры"},
        "fmt_images": {"EN": "Images", "RU": "Изображения"},
        "fmt_texarr": {"EN": "Texture Array", "RU": "Массив текстур"},
        "fmt_nbt": {"EN": "NBT Data", "RU": "NBT Данные"},
    }

    @classmethod
    def get(cls, key: str) -> str:
        return cls.DATA.get(key, {}).get(cls.LANG, key)
