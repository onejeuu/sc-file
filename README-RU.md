# sc-file

<!-- Links -->

[pypi]: https://pypi.org/project/sc-file
[license]: https://opensource.org/licenses/MIT
[build]: https://github.com/onejeuu/sc-file/actions/workflows/build.yml
[issues]: https://github.com/onejeuu/sc-file/issues
[releases]: https://github.com/onejeuu/sc-file/releases
[docs]: https://sc-file.readthedocs.io/en/latest
[readme-en]: README.md

<!-- Docs -->

[docs-usage]: https://sc-file.readthedocs.io/en/latest/usage.html
[docs-faq]: https://sc-file.readthedocs.io/en/latest/faq.html
[docs-formats]: https://sc-file.readthedocs.io/en/latest/formats.html
[docs-support]: https://sc-file.readthedocs.io/en/latest/support.html
[docs-compile]: https://sc-file.readthedocs.io/en/latest/compile.html
[docs-library]: https://sc-file.readthedocs.io/en/latest/api/index.html

<!-- Badges -->

[badge-pypi]: https://img.shields.io/pypi/v/sc-file.svg
[badge-license]: https://img.shields.io/github/license/onejeuu/sc-file
[badge-docs]: https://img.shields.io/readthedocs/sc-file
[badge-build]: https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/build.yml
[badge-issues]: https://img.shields.io/github/issues/onejeuu/sc-file
[badge-en]: https://img.shields.io/badge/translate%20to-English%20%F0%9F%87%AC%F0%9F%87%A7-white

<img src="assets/scfile.svg" alt="icon" width="96" />

[![Pypi][badge-pypi]][pypi] [![License][badge-license]][license] [![Docs][badge-docs]][docs] [![Build][badge-build]][build] [![Issues][badge-issues]][issues]

[![EN][badge-en]][readme-en]

## Overview

**scfile** это утилита и библиотека для парсинга и конвертации ассетов игры stalcraft (например, моделей и текстур) в стандартные форматы.

_этот проект является неофициальным и не имеет отношения к разработчикам stalcraft. все торговые марки и активы принадлежат их соответствующим владельцам._

📚 Документация: [sc-file][docs] \
[Usage][docs-usage] / [FAQ][docs-faq] /
[Game Formats][docs-formats] / [Formats Support][docs-support] /
[Compile Guide][docs-compile] / [Library API Reference][docs-library]

🗂️ Поддерживаемые форматы игры: `.mcsb`, `.mcsa`, `.mcvd`, `.ol`, `.mic`, `.texarr`. \
[Подробнее об игровых форматах...][docs-formats]

💻 Исполняемый файл `scfile.exe` можно скачать на [странице Releases][releases] или [скомпилировать самому][docs-compile] \
[Подробнее об использовании...][docs-usage]

❓ **Почему кодирование обратно в игровые форматы не поддерживается?** \
И другие часто задаваемые вопросы отвечены на [странице FAQ][docs-faq].

## 🛠️ Поддерживаемые форматы

| Тип            | Исходный формат           | Выходной формат                 |
| -------------- | ------------------------- | ------------------------------- |
| 🧊 Модель      | `.mcsb`, `.mcsa`, `.mcvd` | `.obj`, `.glb`, `.dae`, `.ms3d` |
| 🧱 Текстура    | `.ol`                     | `.dds`                          |
| 🖼️ Изображение | `.mic`                    | `.png`                          |
| 📦 Архив       | `.texarr`                 | `.zip`                          |

[Подробнее об поддержке форматов...][docs-support]

## 🚀 Быстрый Старт

Пример команды:

```bash
scfile.exe model.mcsb -F dae --skeleton
```

[Подробнее об использовании...][docs-usage]

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
- `Art3mLapa` - советы, багрепорт.
- `n1kodim` - советы, вклад в проект.
- `IExploitableMan`- вклад в проект.
- `Sarioga` - фидбек, багрепорт.
- `Hazart` - багрепорт.
