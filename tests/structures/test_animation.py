import numpy as np

from scfile.structures.models import AnimationClip


def test_times() -> None:
    clip = AnimationClip(frames=4, rate=0.5)

    assert np.array_equal(clip.times, [0.0, 0.5, 1.0, 1.5])
