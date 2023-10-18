# Converting STALCRAFT Files Library

Library for converting encrypted stalcraft game files, such as models and textures into well-known formats. \
You can use compiled utility from [Releases](https://github.com/onejeuu/sc-file/releases) page.


### Formats

`.mcsa` `->` `.obj` \
`.mic` `->` `.png` \
`.ol` `->` `.dds`


## Install:

### Pip
```console
pip install scfile -U
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

Or

```console
pip install -r requirements.txt
```
</details>

## Usage:

### Simple
```python
from scfile import mcsa_to_obj, mic_to_png, ol_to_dds

mcsa_to_obj("path/to/file.mcsa", "path/to/file.obj")
mic_to_png("path/to/file.mic", "path/to/file.png")
ol_to_dds("path/to/file.ol", "path/to/file.dds")
```

### Advanced
```python
from scfile import McsaFile, MicFile, OlFile
from scfile import BinaryReader

with BinaryReader("path/to/file.ol") as reader:
    ol = OlFile(reader).to_dds()

with open("path/to/file.dds", "wb") as fp:
    fp.write(ol)
```

### CLI Utility

```console
SCF.exe --source path/to/file.mcsa
```

```console
SCF.exe --source path/to/file.ol --output path/to/file.dds
```


## Build:
```console
poetry run build
```
