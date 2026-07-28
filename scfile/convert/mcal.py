"""
MCAL animation export.
"""

from scfile import formats, types
from scfile.structures.models import transforms as T

from .animate import apply_external


def apply_mcal(
    library: types.PathLike,
    model: types.PathLike,
    output: types.OutputLike = None,
) -> None:
    """Export model geometry with MCAL animation clips to GLB."""

    apply_external(
        formats.McalDecoder,
        T.apply_animation_library,
        library,
        model,
        output,
    )
