"""
Format auto-detection by file extension.
"""

from pathlib import Path
from typing import Optional

from scfile import exceptions, types
from scfile.options import Options
from scfile.operations import convert
from scfile.registry import RESOLVER


def format(
    source: types.PathLike,
) -> str:
    """Detect input file format."""

    if spec := RESOLVER.resolve(source):
        return str(spec.format)

    return Path(source).suffix.lower().lstrip(".")


def auto(
    source: types.PathLike,
    output: types.OutputLike = None,
    options: Optional[Options] = None,
) -> list[Path]:
    """
    Automatically convert one file between formats based on its extension.

    Arguments:
        source: Path to source file.
        output (optional): Path to directory. Defaults to same location as source.
        options (optional): Shared handlers options.

    Raises:
        BinaryStructureError: Source file is corrupted.
        UnknownFormatError: Source file format cannot be detected.

    Example:
        - ``auto("model.mcsb", "model.obj")``
        - ``auto("model.mcsb", "model.obj", Options(skeleton=True))``
        - ``auto("model.mcsb", "path/to/output/dir")``
    """

    src_path = Path(source)
    source_spec = RESOLVER.resolve(src_path)
    if source_spec is None or source_spec.decoder is None:
        raise exceptions.UnknownFormatError(str(src_path), src_path.suffix)

    options = options or Options()
    targets = RESOLVER.targets(source_spec, options)
    if not targets:
        raise exceptions.ConversionError(
            f"No standalone output format available for '{source_spec.format}'.",
            location=str(src_path),
        )

    return [convert(source_spec.decoder, encoder, src_path, output, options) for encoder in targets.values()]
