# sc-file

<!-- Links -->

[pypi]: https://pypi.org/project/sc-file
[license]: https://opensource.org/licenses/MIT
[tests]: https://github.com/onejeuu/sc-file/actions/workflows/tests.yml
[build]: https://github.com/onejeuu/sc-file/actions/workflows/release.yml
[issues]: https://github.com/onejeuu/sc-file/issues
[releases]: https://github.com/onejeuu/sc-file/releases
[docs]: https://sc-file.readthedocs.io/ru/latest
[readme-en]: README.md

<!-- Usage -->

[usage-dragndrop]: https://ru.wikipedia.org/wiki/Drag-and-drop
[usage-defaultapp]: https://support.microsoft.com/ru-ru/windows/e5d82cad-17d1-c53b-3505-f10a32e1894d
[usage-cli]: https://ru.wikipedia.org/wiki/Интерфейс_командной_строки
[usage-library]: https://pypi.org/project/sc-file

<!-- Docs -->

[docs-usage]: https://sc-file.readthedocs.io/ru/latest/usage.html
[docs-faq]: https://sc-file.readthedocs.io/ru/latest/faq.html
[docs-formats]: https://sc-file.readthedocs.io/ru/latest/formats.html
[docs-support]: https://sc-file.readthedocs.io/ru/latest/support.html
[docs-compile]: https://sc-file.readthedocs.io/ru/latest/compile.html
[docs-library]: https://sc-file.readthedocs.io/ru/latest/api/index.html

<!-- Badges -->

[badge-pypi]: https://img.shields.io/pypi/v/sc-file.svg
[badge-license]: https://img.shields.io/github/license/onejeuu/sc-file
[badge-docs]: https://img.shields.io/readthedocs/sc-file
[badge-tests]: https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/tests.yml?label=tests
[badge-build]: https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/release.yml?label=build
[badge-issues]: https://img.shields.io/github/issues/onejeuu/sc-file
[badge-en]: https://img.shields.io/badge/translate%20to-🇬🇧%20English-0096FF

<img src="assets/scfile.svg" alt="icon" width="96" />

[![Pypi][badge-pypi]][pypi] [![License][badge-license]][license] [![Docs][badge-docs]][docs] [![Tests][badge-tests]][tests] [![Build][badge-build]][build] [![Issues][badge-issues]][issues]

[![EN][badge-en]][readme-en]

## Обзор

**scfile** это утилита и библиотека для конвертации ассетов игры stalcraft (например, моделей и текстур) в стандартные форматы.

_этот проект является неофициальным и не имеет отношения к разработчикам stalcraft. все торговые марки и активы принадлежат их соответствующим владельцам._

📚 Документация: [sc-file.readthedocs.io][docs] \
[Использование][docs-usage] / [FAQ][docs-faq] / [Игровые Форматы][docs-formats] / [Поддержка Форматов][docs-support] / [Компиляция][docs-compile] / [API Библиотеки][docs-library]

🗂️ Поддерживаемые форматы игры: `.mcsb`, `.mcsa`, `.mcvd`, `.ol`, `.mic`, `.texarr`. \
[Подробнее об игровых форматах...][docs-formats]

💻 Исполняемый файл `scfile.exe` можно скачать на [странице Releases][releases] или [скомпилировать самому][docs-compile] \
[Подробнее об использовании...][docs-usage]

❓ **Почему кодирование обратно в игровые форматы не поддерживается?** \
И другие часто задаваемые вопросы отвечены на [странице FAQ][docs-faq].

## 🛠️ Поддерживаемые форматы

| Тип            | Исходный формат           | Выходной формат                 |
| -------------- | ------------------------- | ------------------------------- |
| 🧊 Модель      | `.mcsb`, `.mcsa`, `.mcvd` | `.glb`, `.obj`, `.dae`, `.ms3d` |
| 🧱 Текстура    | `.ol`                     | `.dds`                          |
| 🖼️ Изображение | `.mic`                    | `.png`                          |
| 📦 Архив       | `.texarr`                 | `.zip`                          |

[Подробнее об поддержке форматов...][docs-support]

## 🚀 Использование

- **Проще всего использовать [Drag & Drop][usage-dragndrop]**. Просто перетащите нужные файлы на `scfile.exe`.
- **Указать `scfile.exe` как [приложение по умолчанию][usage-defaultapp]** для нужных типов файлов.
- **Через терминал как самый обычный [CLI][usage-cli]** для указания параметров.
- **Как [Python библиотеку][usage-library]** для комплексных задач.

Пример команды для терминала:

```bash
scfile.exe model.mcsb -F dae --skeleton
```

[Подробнее об использовании и параметрах...][docs-usage]

## 📖 Библиотека

Чтобы установить библиотеку для разработки, используйте команду:

```bash
pip install sc-file -U
```

Простой пример использования:

```python
from scfile import UserOptions, convert

# Optional convert settings
options = UserOptions(parse_skeleton=True)

# Specific format to format
convert.mcsb_to_obj(source="path/to/model.mcsb", options=options)

# Or auto detect by file suffix
convert.auto(source="path/to/model.mcsb", options=options)
```

[Подробнее об библиотеке...][docs-library]

## 🤝 Благодарности

- `kommunist2021` - разбор структуры файлов.
- `Art3mLapa` - советы, багрепорт, вклад в проект.
- `n1kodim` - советы, вклад в проект.
- `IExploitableMan`- вклад в проект.
- `Sarioga` - фидбек, багрепорт.
- `Hazart` - багрепорт.
