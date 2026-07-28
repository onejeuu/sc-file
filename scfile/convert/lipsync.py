"""
Facial animation export.
"""

from scfile import formats, types
from scfile.structures.models import transforms as T

from .animate import apply_external


def lipsync(
    animation: types.PathLike,
    model: types.PathLike,
    output: types.OutputLike = None,
) -> None:
    """Export model geometry with MCVD facial animations to GLB."""

    apply_external(
        formats.McvdDecoder,
        T.apply_morph_animation,
        animation,
        model,
        output,
    )
