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

<!-- Documentation -->

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

<img src="assets/scfile.svg" alt="sc-file" width="96" />

[![PyPI][badge-pypi]][pypi] [![License][badge-license]][license] [![Docs][badge-docs]][docs] [![Tests][badge-tests]][tests] [![Build][badge-build]][build] [![Issues][badge-issues]][issues]

🇬🇧 **English** | 🇷🇺 [Русский][readme-ru]

**scfile** is a program and library for converting proprietary STALCRAFT assets formats to standard ones.

> This is an **unofficial** project and is **not affiliated** with EXBO.

<!--
keywords: sc scx stalcraft x майн ск сталкрафт
runtime/stalcraft/modassets/assets map_cache/5.0
blender rig anims 3d bones scene unpack decrypt decryptor
блендер риг анимки 3д кости сцена моделька локи распаковать расшифровать дешифратор
-->

## ✨ Supported Formats

| Type             | Game formats                             | →   | Standard formats       |
| ---------------- | ---------------------------------------- | --- | ---------------------- |
| 🧊 **Model**     | `.mcsb`, `.efkmodel`                     | →   | `.obj`, `.glb`, `.fbx` |
| 🌀 **Animation** | `.mcvd` + `.mcsb`,<br/>`.mcal` + `.mcsb` | →   | `.glb`                 |
| 🧱 **Texture**   | `.ol`                                    | →   | `.dds`                 |
| 🖼️ **Image**     | `.mic`                                   | →   | `.png`                 |
| 🗃️ **Archive**   | `.texarr`                                | →   | `.zip`                 |
| 🗺 **Region**     | `.mdat`                                  | →   | `.mca`                 |
| ⚙️ **NBT**       | `itemnames.dat` `common` `prefs` `sd0-4` | →   | `.json`                |

> [Details about formats →][docs-support]

</br>

> [!IMPORTANT]  
> **Reverse conversion (`standard` → `game`) is not available.**  
> [See FAQ for details →][docs-faq]

## 🚀 Usage

### Download executable

Download `scfile.exe` from the [Releases page][releases].

**Usage:**

- **Graphical interface:** launch `scfile.exe`.
- **Drag and drop:** drag files or folders onto `scfile.exe` in File Explorer.
- **Command line:** run `scfile.exe --help` for commands and options.

For example:

```console
scfile.exe model.mcsb -F glb --skeleton
```

This exports the model and its armature to GLB. \
See the [usage guide][docs-usage] for other options.

### Install the Python package

```console
pip install sc-file
pip install sc-file[gui]  # extra graphical interface
```

The base package includes only library and CLI.

### Compile from source

See the [build guide][docs-compile] for development, contributions, and custom builds.

## 📖 Library

Install or update the package:

```console
pip install sc-file -U
```

**Usage example:**

```python
from scfile import convert, formats, Options

# Detect the source format and convert it
convert.auto("model.mcsb", options=Options(skeleton=True))

# Use an explicit conversion and output path
convert.mcsb_to_obj("model.mcsb", "output/model.obj")

# Decode a known format and inspect its data
with formats.McsbDecoder("model.mcsb") as mcsb:
    model = mcsb.decode()

print([mesh.name for mesh in model.scene.meshes])
print([bone.name for bone in model.scene.skeleton.bones])
```

[Complete library documentation →][docs-library]

## 🔗 Links

- `📚` **Documentation:** [sc-file.readthedocs.io][docs]
- `❓` **Questions?** Check [FAQ][docs-faq] or [contact me][contact]
- `🐛` **Found a bug?** [Open an issue][issues]
- `💻` **Download executable:** [Latest release][releases]
- `🔧` **Compile from source:** [Build guide][docs-compile]

## 🤝 Acknowledgments

`kommunist2021` · `Art3mLapa` · `n1kodim` · `TeamDima` · `BoJIwEbNuK7`  
`IExploitableMan` · `tuneyadecc` · `Hazart`

Thanks to everyone who reported issues, shared findings, or contributed ideas.
