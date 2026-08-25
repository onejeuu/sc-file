"""Conversion path management."""

import os
from collections.abc import Collection, Generator
from contextlib import contextmanager
from pathlib import Path
from tempfile import mkstemp

from scfile import exceptions, types
from scfile.enums import OnConflict
from scfile.options import Options


def source(
    value: types.SourceLike,
) -> Path:
    """Require one regular source file."""

    path = Path(value)
    if not path.exists() or not path.is_file():
        raise exceptions.FileNotFound(str(path))

    return path


def output(
    source: Path,
    value: types.OutputLike,
    suffix: str,
    options: Options,
) -> types.ResultPath:
    """Choose an output path under the conflict policy."""

    path = destination(source, value, suffix)
    return select(path, options)


def select(
    path: Path,
    options: Options,
    assigned: Collection[Path] = (),
) -> types.ResultPath:
    """Apply the conflict policy to an exact output path."""

    match options.on_conflict:
        case OnConflict.SKIP if path.exists() or path in assigned:
            return None
        case OnConflict.RENAME:
            return unique(path, assigned)
        case _:
            return path


def destination(
    source: Path,
    output: types.OutputLike,
    suffix: str,
) -> Path:
    """Build the output path and create its parent directory."""

    path = Path(output or source.parent)

    if path.suffix == suffix:
        dest = path
    else:
        dest = path / f"{source.stem}{suffix}"

    dest.parent.mkdir(exist_ok=True, parents=True)
    return dest


def unique(
    path: Path,
    assigned: Collection[Path] = (),
) -> Path:
    """Append a counter when the path already exists."""

    filename, suffix = path.stem, path.suffix
    counter = 1

    while path.exists() or path in assigned:
        path = path.parent / Path(f"{filename} ({counter}){suffix}")
        counter += 1

    return path


@contextmanager
def stage(
    output: Path,
) -> Generator[Path]:
    """Isolate unfinished operation output."""

    fd, name = mkstemp(
        dir=output.parent,
        prefix=f".{output.name}.",
        suffix=".tmp",
    )
    tmp = Path(name)

    try:
        os.close(fd)
        yield tmp
        tmp.replace(output)

    except BaseException as error:
        try:
            tmp.unlink(missing_ok=True)
        except OSError as tmperror:
            error.add_note(f"Could not remove temporary output '{tmp}': {tmperror}")
        raise
