from scfile.content.models import Feature, ModelMeta


def test_declared_features() -> None:
    meta = ModelMeta(flags={Feature.UV: True})

    assert meta.declares(Feature.UV)
    assert not meta.declares(Feature.NORMALS)
