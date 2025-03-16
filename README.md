# sc-file 4.0 [WIP]

[![Pypi](https://img.shields.io/pypi/v/sc-file.svg)](https://pypi.org/project/sc-file)
[![License](https://img.shields.io/github/license/onejeuu/sc-file)](https://opensource.org/licenses/MIT)
[![Build](https://img.shields.io/github/actions/workflow/status/onejeuu/sc-file/build.yml)](https://github.com/onejeuu/sc-file/actions/workflows/build.yml)
[![Issues](https://img.shields.io/github/issues/onejeuu/sc-file)](https://github.com/onejeuu/sc-file/issues)

> [!CAUTION]
> Work In Progress. Functionality may be missing or malfunctioning.

[Перевод на русский](README_RU.md)

**scfile** is a utility and library designed for decoding and converting STALCRAFT asset files, such as models and textures, into popular formats.

Supported formats: `.mcsb`, `.mcsa`, `.ol`, `.mic`.

Executable utility `scfile.exe` can be downloaded from [Releases page](https://github.com/onejeuu/sc-file/releases) or [compiled from source](https://github.com/onejeuu/sc-file/tree/4.0-dev?tab=readme-ov-file#%EF%B8%8F-build).

❓ [Why reverse encoding into game formats is unsupported?](https://github.com/onejeuu/sc-file/blob/4.0-dev/FAQ.md#q-how-to-encode-files-back-into-game-formats)

🗂 For answers to other common questions, please refer to [FAQ page](FAQ.md).

## 📚 Library

### Install

```bash
pip install sc-file -U
```

## 📁 Formats

| Type    | Source       | Output                  |
| ------- | ------------ | ----------------------- |
| Model   | .mcsb, .mcsa | .obj, .dae, .glb, .ms3d |
| Texture | .ol          | .dds                    |
| Image   | .mic         | .png                    |

### Models

- Versions supported: 7.0, 8.0, 10.0, 11.0

### Textures

- Formats supported: DXT1, DXT3, DXT5, RGBA8, BGRA8, DXN_XY
- Formats unsupported: RGBA32F
- Some normal map textures can be inverted

## 🛠️ Build

1. Download project

   ```bash
   git clone https://github.com/onejeuu/sc-file.git
   ```

   ```bash
   cd sc-file
   ```

2. Recommended to create virtual environment

   ```bash
   python -m venv .venv
   ```

   ```bash
   .venv\Scripts\activate
   ```

3. Install dependencies

   via poetry

   ```bash
   poetry install
   ```

   or via pip

   ```bash
   pip install -r requirements.txt
   ```

4. Run script to compile

   ```bash
   python scripts/build.py
   ```

   Executable file `scfile.exe` will be created in `/dist` directory.
