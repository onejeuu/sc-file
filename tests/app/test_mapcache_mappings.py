import json

import pytest

from scfile.app.mapcache import load_block_mappings
from scfile.exceptions import BlockMappingError
from scfile.formats.mca.mappings import RESOURCEPACK, VANILLA


def test_load_builtin_and_ordered_json_layers(tmp_path):
    custom = tmp_path / "custom.json"
    custom.write_text(json.dumps({"42": 73}), encoding="utf-8")

    layers = load_block_mappings(("vanilla", str(custom), '{"42":91}'))

    assert layers is not None
    assert layers[0] is VANILLA
    assert layers[1] == {42: 73}
    assert layers[2] == {42: 91}


def test_no_cli_layers_leaves_default_selection_to_options():
    assert load_block_mappings(()) is None


def test_builtin_resourcepack_can_be_selected_explicitly():
    layers = load_block_mappings(("resourcepack",))

    assert layers == (RESOURCEPACK,)


def test_invalid_json_mapping_is_rejected():
    with pytest.raises(BlockMappingError):
        load_block_mappings(('{"4096":1}',))


def test_non_integer_target_is_rejected():
    with pytest.raises(BlockMappingError):
        load_block_mappings(('{"42":"73"}',))
