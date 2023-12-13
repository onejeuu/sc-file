# Converting STALCRAFT Files

Library for converting encrypted stalcraft game files, such as models and textures into well-known formats.

You can use compiled cli utility from [Releases](https://github.com/onejeuu/sc-file/releases) page.


## ⚠️ Disclaimer
**Do not use game assets directory directly. <ins>You can get banned for any changes in game client</ins>. Copy files you need to another folder and work there.**


## Formats

`.mcsa` `->` `.obj` \
`.mic` `->` `.png` \
`.ol` `->` `.dds`


<br>


# CLI Utility

## Usage

```bash
scfile [OPTIONS] [FILES]...
```

### Arguments

`FILES`: **List of file paths to be converted**. Multiple files should be separated by **spaces**. Accepts both full and relative paths. **Does not accept directory**.

### Options

`-O` `--output`: **<ins>One</ins> path to output file or directory**. Can be specified multiple times for different output files or directories. If not specified, file will be saved in same directory with new suffix. You can specify multiple `FILES` and single `--output` directory.

### Examples

1. Convert single file:
    ```bash
    scfile file.mcsa
    ```
    Will be saved in same directory with new suffix.

1. Convert single file with specified path:
    ```bash
    scfile file.mcsa --output path/to/file.obj
    ```

1. Convert multiple files to specified directory:
    ```bash
    scfile file1.mcsa file2.mcsa --output path/to/folder
    ```

1. Convert multiple files with explicitly specified output files:
    ```bash
    scfile file1.mcsa file2.mcsa -O 1.obj -O 2.obj
    ```
    If count `FILES` and `-O` is different, as many files as possible will be converted.

1. Convert all `.mcsa` files in current directory:
    ```bash
    scfile *.mcsa
    ```
    In this case `-O` accepts only directory.
    Subfolders are not included.

2. Convert all `.mcsa` files with subfolders to specified directory:
    ```bash
    scfile **/*.mcsa -O path/to/folder
    ```
    In this case `-O` accepts only directory.
    With `-O` specified, folder structure is not duplicated.


<br>


# Library

## Install

### Pip
```console
pip install sc-file -U
```

<details>
<summary>Manual</summary>

```console
git clone git@github.com:onejeuu/sc-file.git
```

```console
cd sc-file
```

```console
poetry install
```
</details>

## Usage

### Simple
```python
from scfile import convert

convert.mcsa_to_obj("path/to/file.mcsa", "path/to/file.obj")
convert.mic_to_png("path/to/file.mic", "path/to/file.png")
convert.ol_to_dds("path/to/file.ol", "path/to/file.dds")
```

### Advanced
```python
from scfile import McsaFile

with McsaFile("path/to/file.mcsa") as mcsa:
    obj = mcsa.to_obj()

with open("path/to/file.obj", "wb") as fp:
    fp.write(obj)
```

## Build

```bash
poetry install
```

```bash
poetry run build
```
