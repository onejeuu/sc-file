# sc-file

<!-- Links -->

[pypi]: https://pypi.org/project/sc-file
[license]: https://opensource.org/licenses/MIT
[build]: https://github.com/onejeuu/sc-file/actions/workflows/release.yml
[issues]: https://github.com/onejeuu/sc-file/issues
[releases]: https://github.com/onejeuu/sc-file/releases
[docs]: https://sc-file.readthedocs.io/en/latest
[readme-ru]: README-RU.md

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
[badge-build]: https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/release.yml
[badge-issues]: https://img.shields.io/github/issues/onejeuu/sc-file
[badge-ru]: https://img.shields.io/badge/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4%20%D0%BD%D0%B0-%F0%9F%87%B7%F0%9F%87%BA%20%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9%20-0096FF

<img src="assets/scfile.svg" alt="icon" width="96" />

[![Pypi][badge-pypi]][pypi] [![License][badge-license]][license] [![Docs][badge-docs]][docs] [![Build][badge-build]][build] [![Issues][badge-issues]][issues]

[![RU][badge-ru]][readme-ru]

## Overview

**scfile** is a utility and library for parsing and converting stalcraft assets (such as models and textures), into standard formats.

_this project is unofficial and not related to stalcraft devs. all trademarks and assets belong to their respective owners._

📚 Documentation: [sc-file][docs] \
[Usage][docs-usage] / [FAQ][docs-faq] /
[Game Formats][docs-formats] / [Formats Support][docs-support] /
[Compile Guide][docs-compile] / [Library API Reference][docs-library]

🗂️ Supported game formats: `.mcsb`, `.mcsa`, `.mcvd`, `.ol`, `.mic`, `.texarr`. \
[More about Game Formats...][docs-formats]

💻 Executable utility `scfile.exe` can be downloaded from [Releases page][releases] or [compiled from source][docs-compile] \
[More about Usage...][docs-usage]

❓ **Why reverse encoding into game formats is unsupported?** \
And other common questions are answered on [FAQ page][docs-faq].

## 🛠️ Supported Formats

| Type       | Source                    | Output                          |
| ---------- | ------------------------- | ------------------------------- |
| 🧊 Model   | `.mcsb`, `.mcsa`, `.mcvd` | `.obj`, `.glb`, `.dae`, `.ms3d` |
| 🧱 Texture | `.ol`                     | `.dds`                          |
| 🖼️ Image   | `.mic`                    | `.png`                          |
| 📦 Archive | `.texarr`                 | `.zip`                          |

[More about Formats Support…][docs-support]

## 🚀 Quick Start

Command example:

```bash
scfile.exe model.mcsb -F dae --skeleton
```

[More about Usage...][docs-usage]

## 📖 Library

To install library for coding, use following command:

```bash
pip install sc-file -U
```

Simple usage example:

```python
from scfile import UserOptions, convert

# Optional convert settings
options = UserOptions(parse_skeleton=True)

# Specific format to format
convert.mcsb_to_obj(source="path/to/model.mcsb", options=options)

# Or auto detect by file suffix
convert.auto(source="path/to/model.mcsb", options=options)
```

[More details about Library...][docs-library]

## 🤝 Acknowledgments

- `kommunist2021` – file structure research.
- `Art3mLapa` – advice, bug reports, contribution.
- `n1kodim` – advice, contribution.
- `IExploitableMan` – contribution.
- `Sarioga` – feedback, bug reports.
- `Hazart` – bug reports.
