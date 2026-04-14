from PyInstaller.utils.hooks import collect_data_files


hiddenimports = [
    "rich._unicode_data",
    "rich._unicode_data.unicode17-0-0",
]

datas = collect_data_files("rich")
