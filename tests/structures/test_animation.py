import numpy as np

from scfile.structures import models as S


def test_times():
    clip = S.AnimationClip(frames=4, rate=0.5)
    expected = np.array([0.0, 0.5, 1.0, 1.5], dtype=np.float32)
    assert np.allclose(clip.times, expected)
