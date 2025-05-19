"""
Numpy vectors annotation.
"""

from typing import Annotated

import numpy as np
from numpy.typing import NDArray


Vector2D = Annotated[NDArray[np.float32], (..., 2)]
Vector3D = Annotated[NDArray[np.float32], (..., 3)]
Vector4D = Annotated[NDArray[np.float32], (..., 4)]

LinksIds = Annotated[NDArray[np.uint8], (..., 4)]
LinksWeights = Annotated[NDArray[np.float32], (..., 4)]

Polygons = Annotated[NDArray[np.uint32], (..., 3)]
