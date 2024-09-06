# SC FILE

Utility and Library for decoding and converting stalcraft asset files, such as models and textures, into popular formats.

Designed for artworks creation.

For answers to common questions, please refer to [FAQ section](FAQ.md).

You can download executable from [Releases page](https://github.com/onejeuu/sc-file/releases).

![Build](https://github.com/onejeuu/sc-file/actions/workflows/build.yml/badge.svg)

> [!WARNING]
> Do not use game assets directly. \
> Any changes in game client can be detected.

## 📁 Formats

| Type    | Source        | Output                 |
| ------- | ------------- | ---------------------- |
| Model   | .mcsa / .mcvd | .obj, .dae, ms3d, .txt |
| Texture | .ol           | .dds                   |
| Image   | .mic          | .png                   |

### Models

- Versions supported: 7.0, 8.0, 10.0, 11.0
- Skeleton and Animations currently unsupported

### Textures

- Formats supported: DXT1, DXT3, DXT5, RGBA8, BGRA8, DXN_XY
- Formats supported partially: Cubemaps (HDRI)
- Formats unsupported: RGBA32F
- Some normal map textures can be inverted

## 💻 CLI Utility

From bash:

```bash
scfile [FILES]... [OPTIONS]
```

> [!TIP]
> You can just drag and drop one or multiple files onto `scfile.exe`.

### Arguments

- `FILES`: **List of file paths to be converted**. Multiple files should be separated by **spaces**. Accepts both full and relative paths. Only one directory can be specified.

### Options

- `-F`, `--formats`: **Preferred format for models**. To specify multiple formats, **option** must be used multiple times.
- `-O`, `--output`: **One path to output directory**. If not specified, file will be saved in same directory with a new suffix.

### Flags

- `--subdir`: Recreates input subdirectories to output directory.
- `--no-overwrite`: Do not overwrite output file if already exists.
- `--silent`: Suppress all console prints.

### Examples

1. Convert model with specified formats

   ```bash
   scfile model.mcsa -F obj -F dae
   ```

   _Will be saved in same location with a new suffix._

2. Convert multiple files to a specified directory:

   ```bash
   scfile model1.mcsa model2.mcsa -O path/to/output
   ```

3. Convert all `.mcsa` files in current directory:

   ```bash
   scfile *.mcsa
   ```

   _Will be saved in same location. Subdirectories are not included._

4. Convert all `.mcsa` files with subdirectories to a specified directory:

   ```bash
   scfile path/to/files/**/*.mcsa -O path/to/output --subdir
   ```

## 📚 Library

### Install

```bash
pip install sc-file -U
```

### Usage

#### Simple Method

```python
from scfile import convert

# Output path is optional.
# Defaults to source path with new suffix.
convert.mcsa_to_obj("path/to/model.mcsa", "path/to/model.obj")
convert.ol_to_dds("path/to/texture.ol", "path/to/texture.dds")
convert.mic_to_png("path/to/image.mic", "path/to/image.png")

# Skeleton support via MilkShape3D
convert.mcsa_to_ms3d("path/to/model.mcsa", "path/to/model.ms3d")
convert.mcsa_to_ms3d_ascii("path/to/model.mcsa", "path/to/model.txt")

# Or determinate it automatically
convert.auto("path/to/model.mcsa")
```

#### Advanced Examples

- Default usage

```python
from scfile.file.data import ModelData
from scfile.file import McsaDecoder, ObjEncoder

mcsa = McsaDecoder("model.mcsa")
data: ModelData = mcsa.decode()
mcsa.close() # ? Necessary to close decoder

obj = ObjEncoder(data)
obj.encode().save("model.obj") # ? Buffer closes after save
```

- Use encoded content bytes

```python
obj = ObjEncoder(data) # ? data - ModelData from McsaDecoder
obj.encode() # ? Write bytes into buffer

with open("model.obj", "wb") as fp:
    fp.write(obj.content) # ? obj.content - Encoder buffer bytes

obj.close() # ? Necessary to close encoder
```

- Use convert methods

> [!IMPORTANT]
> Unclosed buffer can cause memory leaks. \
> When using `convert_to` or `to_xxx` methods, encoder buffer remains open. \
> `close()` or `save()` or another context (`with`) **is necessary**.

```python
mcsa = McsaDecoder("model.mcsa")
mcsa.convert_to(ObjEncoder).save("model.obj") # ? Encoder buffer closes after save
mcsa.close() # ? Necessary to close decoder
```

```python
mcsa = McsaDecoder("model.mcsa")
mcsa.to_obj().save("model.obj") # ? Encoder buffer closes after save
mcsa.close() # ? Necessary to close decoder
```

- Use context manager (`with`)

```python
with McsaDecoder("model.mcsa") as mcsa:
    data: ModelData = mcsa.decode()

with ObjEncoder(data) as obj:
    obj.encode().save("model.obj")
```

- Use context manager + convert methods

```python
with McsaDecoder("model.mcsa") as mcsa:
    obj = mcsa.convert_to(ObjEncoder)
    obj.close() # ? Necessary to close encoder
```

or

```python
with McsaDecoder("model.mcsa") as mcsa:
    mcsa.to_obj().save("model.obj") # ? Encoder buffer closes after save
```

- Save multiple copies

```python
with McsaDecoder("model.mcsa") as mcsa:
    with mcsa.to_obj() as obj:
        obj.save_as("model_1.obj") # ? Encoder buffer remains open after save_as
        obj.save_as("model_2.obj")
    # ? Encoder buffer closes after end of context (with)
```

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
