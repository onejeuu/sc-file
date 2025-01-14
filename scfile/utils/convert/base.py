import pathlib
from typing import Optional, Type

from scfile.core import FileDecoder, FileEncoder
from scfile.core.decoder import Opener
from scfile.core.types import Context, Options
from scfile.io.types import PathLike


def convert(
    decoder: Type[FileDecoder[Opener, Context, Options]],
    encoder: Type[FileEncoder[Context, Options]],
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
    overwrite: bool = True,
):
    src_path = pathlib.Path(source)
    out_path = pathlib.Path(output or source)

    if not src_path.exists() or not src_path.is_file():
        raise Exception("Source path not exists")

    if not out_path.parent.exists():
        out_path.parent.mkdir(exist_ok=True, parents=True)

    with decoder(file=src_path, options=options) as src:
        with src.convert_to(encoder=encoder) as out:
            output = out_path.with_suffix(out.suffix)

            if not overwrite:
                output = ensure_unique_path(path=output, suffix=out.suffix)

            out.save(path=output)


def ensure_unique_path(path: pathlib.Path, suffix: str) -> pathlib.Path:
    filename = path.stem
    counter = 1

    while path.exists():
        path = path.parent / pathlib.Path(f"{filename} ({counter}){suffix}")
        counter += 1

    return path
