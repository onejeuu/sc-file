# sc-file

<!-- Links -->

[readme-ru]: README-RU.md
[pypi]: https://pypi.org/project/sc-file
[license]: https://opensource.org/licenses/MIT
[tests]: https://github.com/onejeuu/sc-file/actions/workflows/tests.yml
[build]: https://github.com/onejeuu/sc-file/actions/workflows/release.yml
[issues]: https://github.com/onejeuu/sc-file/issues
[releases]: https://github.com/onejeuu/sc-file/releases
[docs]: https://sc-file.readthedocs.io/en/latest
[contact]: https://onejeuu.t.me

<!-- Usage -->

[usage-dragndrop]: https://en.wikipedia.org/wiki/Drag_and_drop
[usage-defaultapp]: https://support.microsoft.com/en-us/windows/e5d82cad-17d1-c53b-3505-f10a32e1894d
[usage-cli]: https://en.wikipedia.org/wiki/Command-line_interface

<!-- Docs -->

[docs-usage]: https://sc-file.readthedocs.io/en/latest/usage.html
[docs-faq]: https://sc-file.readthedocs.io/en/latest/faq.html
[docs-support]: https://sc-file.readthedocs.io/en/latest/support.html
[docs-compile]: https://sc-file.readthedocs.io/en/latest/compile.html
[docs-library]: https://sc-file.readthedocs.io/en/latest/api/index.html

<!-- Badges -->

[badge-pypi]: https://img.shields.io/pypi/v/sc-file.svg
[badge-license]: https://img.shields.io/github/license/onejeuu/sc-file
[badge-docs]: https://img.shields.io/readthedocs/sc-file
[badge-tests]: https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/tests.yml?label=tests
[badge-build]: https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/release.yml?label=build
[badge-issues]: https://img.shields.io/github/issues/onejeuu/sc-file

<img src="assets/scfile.svg" alt="icon" width="96" />

[![Pypi][badge-pypi]][pypi] [![License][badge-license]][license] [![Docs][badge-docs]][docs] [![Tests][badge-tests]][tests] [![Build][badge-build]][build] [![Issues][badge-issues]][issues]

🇬🇧 **English** | 🇷🇺 [Русский][readme-ru]

## Overview

**scfile** is a utility and library for converting proprietary Stalcraft assets formats to standard ones.

> This is an **unofficial** project and is **not affiliated** with EXBO.

## ✨ Supported Formats

| Type           | Game formats            | →   | Standard formats             |
| -------------- | ----------------------- | --- | ---------------------------- |
| 🧊 **Model**   | `.mcsb` `.mcsa` `.mcvd` | →   | `.glb` `.obj` `.dae` `.ms3d` |
| 🧱 **Texture** | `.ol`                   | →   | `.dds`                       |
| 🖼️ **Image**   | `.mic`                  | →   | `.png`                       |
| 📦 **Archive** | `.texarr`               | →   | `.zip`                       |
| ⚙️ **Data**    | `NBT`\*                 | →   | `.json`                      |

\* `NBT` refers to specific files (`itemnames.dat`, `prefs`, `sd0`, etc.)

> [!TIP]  
> 📚 [Detailed formats support →][docs-support]

</br>

> [!IMPORTANT]  
> **Reverse conversion (`standard` → `game`) is not available.**  
> 📚 [See FAQ for details →][docs-faq]

## 🚀 Installation

> **Three ways to get started:** download, install, or compile.

### 💻 Download executable

Standalone `scfile.exe` available on [Releases page][releases].  
_No Python required._

**Usage:**

- 📥 **Drag & Drop**: drag file onto `scfile.exe`  
   _[What is drag and drop?][usage-dragndrop]_
- 🖱️ **Open With**: set as default app for supported formats  
   _[How to set default app (Windows)?][usage-defaultapp]_
- 📟 **Command Line**: `scfile.exe --help`  
   _[What is command line interface?][usage-cli]_  
   _Example:_ `scfile.exe model.mcsb -F glb --skeleton`  
   _Options: `-F` picks model format, `--skeleton` extracts model armature._

### 🐍 Install Python package

**Install:**

```bash
pip install sc-file
```

**Usage:**

- 📖 **Python library**: [See Library section](#-library)
- 📟 **CLI via package**: `scfile --help`

### 🔧 Compile from source

Build from source code using the [compile guide][docs-compile].  
_For developers, contributors, or custom builds._

</br>

> [!TIP]  
> 📚 [Usage guide and CLI options →][docs-usage]

## 📖 Library

**Install latest version:**

```bash
pip install sc-file -U
```

**Usage example:**

```py
from scfile import convert, formats, UserOptions

# Simple conversion (auto detect format by file suffix)
# User options to control parsing and export settings
convert.auto("model.mcsb", options=UserOptions(parse_skeleton=True))

# Advanced control (manual decoding and data inspection)
# Context manager ensures proper resource cleanup
with formats.mcsb.McsbDecoder("model.mcsb") as mcsb:
    # Access parsed scene data: meshes, bones
    scene = mcsb.decode().scene
    print(f"Model total vertices: {sum(m.count.vertices for m in scene.meshes)}")

    # Export to a specific standard format
    mcsb.to_obj().save("output.obj")
```

</br>

> [!TIP]  
> 📚 [Complete Library API reference →][docs-library]

## 🔗 Links

- `📚` **Documentation:** [sc-file.readthedocs.io][docs]
- `❓` **Questions?** Check [FAQ][docs-faq] or [contact me][contact]
- `🐛` **Found a bug?** [Open an issue][issues]
- `💻` **Download executable:** [Latest release][releases]
- `🔧` **Compile from source:** [Build guide][docs-compile]

## 🤝 Acknowledgments

`kommunist2021` · `Art3mLapa` · `n1kodim` · `TeamDima` · `BoJIwEbHuK7`  
`IExploitableMan` · `tuneyadecc` · `Hazart`

Thanks to everyone who reported issues, shared findings, or contributed ideas.
