# SC FILE

Library and Utility for converting encrypted stalcraft game files, such as models and textures into well-known formats.

You can use executable utility from [Releases](https://github.com/onejeuu/sc-file/releases) page.

> [!WARNING]
> Do not use game assets directly.
> You can get banned for any changes in game client.

# 📁 Formats

| Type    | Source format | Output format |
| ------- | ------------- | ------------- |
| Model   | .mcsa         | .obj          |
| Texture | .ol           | .dds          |
| Image   | .mic          | .png          |

# 💻 CLI Utility

## Usage

You can drag and drop one or multiple files to `scfile.exe`.

From bash:

```bash
scfile [OPTIONS] [FILES]...
```

## Arguments

- `FILES`: **List of file paths to be converted**. Multiple files should be separated by **spaces**. Accepts both full and relative paths. **Does not accept directory**.

## Options

- `-O`, `--output`: **One path to output file or directory**. Can be specified multiple times for different output files or directories. If not specified, file will be saved in the same directory with a new suffix. You can specify multiple `FILES` and a single `--output` directory.

## Examples

1. Convert a single file:

   ```bash
   scfile file.mcsa
   ```

   _Will be saved in the same directory with a new suffix._

1. Convert a single file with a specified path or name:

   ```bash
   scfile file.mcsa --output path/to/file.obj
   ```

1. Convert multiple files to a specified directory:

   ```bash
   scfile file1.mcsa file2.mcsa --output path/to/dir
   ```

1. Convert multiple files with explicitly specified output files:

   ```bash
   scfile file1.mcsa file2.mcsa -O 1.obj -O 2.obj
   ```

   _If the count of `FILES` and `-O` is different, as many files as possible will be converted._

1. Convert all `.mcsa` files in the current directory:

   ```bash
   scfile *.mcsa
   ```

   _In this case, `-O` accepts only a directory. Subdirectories are not included._

1. Convert all `.mcsa` files with subdirectories to a specified directory:

   ```bash
   scfile **/*.mcsa -O path/to/dir
   ```

   _In this case, `-O` accepts only a directory. With `-O` specified, directory structure is not duplicated._

# 📚 Library

## Install

### Pip

```bash
pip install sc-file -U
```

### Manual

```bash
git clone git@github.com:onejeuu/sc-file.git
```

```bash
cd sc-file
```

```bash
poetry install
```

## Usage

### Simple

```python
from scfile import convert

# Output path is optional.
# Defaults to source path with new suffix.
convert.mcsa_to_obj("path/to/model.mcsa", "path/to/model.obj")
convert.ol_to_dds("path/to/texture.ol", "path/to/texture.dds")
convert.mic_to_png("path/to/image.mic", "path/to/image.png")

# Or determinate it automatically
convert.auto("path/to/model.mcsa")
```

### Advanced

Default

```python
from scfile.file.data import ModelData
from scfile.file.mcsa.decoder import McsaDecoder
from scfile.file.obj.encoder import ObjEncoder

mcsa = McsaDecoder("model.mcsa")
data: ModelData = mcsa.decode()
mcsa.close() # ? Necessary to close

obj = ObjEncoder(data)
obj.encode().save("model.obj") # ? Encoder closes after saving
```

Use encoding content bytes

```python
obj = ObjEncoder(data)
obj.encode()

with open("model.obj", "wb") as fp:
    fp.write(obj.content)

obj.close() # ? Necessary to close
```

Use convert methods

```python
mcsa = McsaDecoder("model.mcsa")
mcsa.convert_to(ObjEncoder).save("model.obj")
mcsa.close()
```

```python
mcsa = McsaDecoder("model.mcsa")
mcsa.to_obj().save("model.obj")
mcsa.close() # ? Necessary to close
```

Use context manager (no need to manual close)

```python
with McsaDecoder("model.mcsa") as mcsa:
    data: ModelData = mcsa.decode()

with ObjEncoder(data) as obj:
    obj.encode().save("model.obj")
```

Use context manager + convert methods

```python
with McsaDecoder("model.mcsa") as mcsa:
    mcsa.to_obj().save("model.obj")
```

# 🛠️ Build

> [!IMPORTANT]
> You will need poetry to do compilation. Install it [here](https://python-poetry.org).

> [!TIP]
> Before proceeding, it's recommended to create virtual environment
>
> ```bash
> poetry shell
> ```

Then install dependencies:

```bash
poetry install
```

And run script to compile:

```bash
poetry run build
```

Executable file will be created in `/dist` directory.
