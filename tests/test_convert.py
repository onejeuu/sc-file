from pathlib import Path

import numpy as np

from scfile.convert import manual
from scfile.convert.animation import _apply_skins
from scfile.core import ModelContent
from scfile.enums import FileFormat
from scfile.options import Options
from scfile.structures import models as S
from tests.conftest import BytesDecoder, BytesEncoder


class PngEncoder(BytesEncoder):
    format = FileFormat.PNG


def test_manual_writes_path(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    result = manual(BytesDecoder, PngEncoder, source, output)

    assert result == output
    assert output.read_bytes() == b"HXGNdata"


def test_manual_returns_none_when_skipped(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")
    output.write_bytes(b"existing")

    result = manual(BytesDecoder, PngEncoder, source, output, Options(on_conflict="skip"))

    assert result is None
    assert output.read_bytes() == b"existing"


def test_manual_renames_conflicting_output(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")
    output.write_bytes(b"existing")

    result = manual(BytesDecoder, PngEncoder, source, output, Options(on_conflict="rename"))

    assert result == tmp_path / "output (1).png"
    assert result is not None
    assert output.read_bytes() == b"existing"
    assert result.read_bytes() == b"HXGNdata"


def test_assembled_skins() -> None:
    def mesh(name: str) -> S.ModelMesh:
        return S.ModelMesh(
            name=name,
            links_ids=np.zeros((1, 4), dtype=np.uint8),
            links_weights=np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32),
        )

    animation = ModelContent(
        scene=S.ModelScene(
            meshes=[mesh("animation")],
            skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(id=0, name="root")]),
        )
    )
    model = ModelContent(
        scene=S.ModelScene(
            meshes=[mesh("hands")],
            skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(id=0, name="root")]),
        )
    )
    scene = S.ModelScene(meshes=[*animation.scene.meshes, *model.scene.meshes], skeleton=animation.scene.skeleton)

    result = _apply_skins(scene, animation, model)

    assert [mesh.skin for mesh in result.meshes] == [0, 1]
    assert len(result.skins) == 2
    assert not scene.skins
