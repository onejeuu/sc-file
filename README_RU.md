# SC FILE 4.0 [WIP]

[![Pypi](https://img.shields.io/pypi/v/sc-file.svg)](https://pypi.org/project/sc-file)
[![License](https://img.shields.io/github/license/onejeuu/sc-file)](https://opensource.org/licenses/MIT)
[![Build](https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/build.yml)](https://github.com/onejeuu/sc-file/actions/workflows/build.yml)
[![Issues](https://img.shields.io/github/issues/onejeuu/sc-file)](https://github.com/onejeuu/sc-file/issues)

> [!CAUTION]
> Работа продолжается. Функционал может отсутствовать или работать неправильно.

Утилита и библиотека для декодирования и конвертирования ассетов игры stalcraft, таких как модели и текстуры, в популярные форматы.

Ответы на распространенные вопросы можно найти в разделе [FAQ](FAQ_RU.md).

Утилиту `scfile.exe` можно скачать со страницы [Releases](https://github.com/onejeuu/sc-file/releases) или скомпилировать самому.

> [!WARNING]
> Любые изменения в ассетах игры могут быть отслежены. Используйте на свой страх и риск.

## 📚 Библиотека

### Установка

```bash
pip install sc-file -U
```

## 📁 Форматы

| Тип         | Исходный      | Output                  |
| ----------- | ------------- | ----------------------- |
| Модель      | .mcsa / .mcvd | .obj, .dae, .glb, .ms3d |
| Текстура    | .ol           | .dds                    |
| Изображение | .mic          | .png                    |

### Модели

- Поддерживаемые версии: 7.0, 8.0, 10.0, 11.0

### Textures

- Поддерживаемые форматы: DXT1, DXT3, DXT5, RGBA8, BGRA8, DXN_XY
- Неподдерживаемые форматы: RGBA32F
- Некоторые текстуры карт нормалей могут быть инвертированы

## 🛠️ Сборка

1. Скачайте проект

   ```bash
   git clone https://github.com/onejeuu/sc-file.git
   ```

   ```bash
   cd sc-file
   ```

2. Рекомендуется создать виртуальную среду

   ```bash
   python -m venv .venv
   ```

   ```bash
   .venv\Scripts\activate
   ```

3. Установите зависимости

   через poetry

   ```bash
   poetry install
   ```

   или через pip

   ```bash
   pip install -r requirements.txt
   ```

4. Запустите скрипт для компиляции

   ```bash
   python scripts/build.py
   ```

   В директории `/dist` будет создан исполняемый файл `scfile.exe`
