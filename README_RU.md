# sc-file 4.0 [WIP]

[![Pypi](https://img.shields.io/pypi/v/sc-file.svg)](https://pypi.org/project/sc-file)
[![License](https://img.shields.io/github/license/onejeuu/sc-file)](https://opensource.org/licenses/MIT)
[![Build](https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/build.yml)](https://github.com/onejeuu/sc-file/actions/workflows/build.yml)
[![Issues](https://img.shields.io/github/issues/onejeuu/sc-file)](https://github.com/onejeuu/sc-file/issues)

> [!CAUTION]
> Работа продолжается. Функционал может отсутствовать или работать неправильно.

**scfile** это утилита и библиотека для декодирования и конвертирования ассетов STALCRAFT, таких как модели и текстуры, в популярные форматы.

Поддерживаемые форматы: `.mcsb`, `.mcsa`, `.ol`, `.mic`.

Утилиту `scfile.exe` можно скачать на [странице Releases](https://github.com/onejeuu/sc-file/releases) или [скомпилировать самому](https://github.com/onejeuu/sc-file/blob/4.0-dev/README_RU.md#%EF%B8%8F-%D1%81%D0%B1%D0%BE%D1%80%D0%BA%D0%B0).

❓ [Почему кодирование обратно в игровые форматы не поддерживается?](https://github.com/onejeuu/sc-file/blob/4.0-dev/FAQ_RU.md#%D0%B2-%D0%BA%D0%B0%D0%BA-%D0%B7%D0%B0%D0%BA%D0%BE%D0%B4%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-%D1%84%D0%B0%D0%B9%D0%BB-%D0%BE%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D0%BE-%D0%B2-%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82-%D0%B8%D0%B3%D1%80%D1%8B)

🗂 Ответы на другие часто задаваемые вопросы можно найти на [странице FAQ](FAQ_RU.md).

## 📚 Библиотека

### Установка

```bash
pip install sc-file -U
```

## 📁 Форматы

| Тип         | Исходный     | Результат               |
| ----------- | ------------ | ----------------------- |
| Модель      | .mcsb, .mcsa | .obj, .dae, .glb, .ms3d |
| Текстура    | .ol          | .dds                    |
| Изображение | .mic         | .png                    |

### Модели

- Поддерживаемые версии: 7.0, 8.0, 10.0, 11.0

### Текстуры

- Поддерживаемые форматы: DXT1, DXT3, DXT5, RGBA8, BGRA8, DXN_XY
- Неподдерживаемые форматы: RGBA32F
- Некоторые текстуры карт нормалей могут быть инвертированы

## 🛠️ Сборка

> [!IMPORTANT]
> Инструкции написаны под [инструмент uv](https://github.com/astral-sh/uv).

1. Скачайте проект

   ```bash
   git clone https://github.com/onejeuu/sc-file.git
   ```

   ```bash
   cd sc-file
   ```

2. Рекомендуется создать виртуальную среду

   ```bash
   uv venv
   ```

   ```bash
   .venv\Scripts\activate
   ```

3. Установите зависимости

   ```bash
   uv sync
   ```

4. Запустите скрипт для компиляции

   ```bash
   uv run scripts/build.py
   ```

   В директории `/dist` будет создан исполняемый файл `scfile.exe`
