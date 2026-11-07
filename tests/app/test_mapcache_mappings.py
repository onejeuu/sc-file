import json

import pytest

from scfile.app.mapcache import load_block_mappings
from scfile.exceptions import BlockMappingError
from scfile.formats.mca.mappings import RESOURCEPACK, VANILLA, compile


def test_load_builtin_and_ordered_json_layers(tmp_path):
    custom = tmp_path / "custom.json"
    custom.write_text(json.dumps({"42": "73"}), encoding="utf-8")

    layers = load_block_mappings(("vanilla", str(custom), '{"42":"91"}'))

    assert layers is not None
    assert layers[0] is VANILLA
    assert layers[1] == {"42": "73"}
    assert layers[2] == {"42": "91"}
    assert compile(layers).ids[42] == 91


def test_no_cli_layers_leaves_default_selection_to_options():
    assert load_block_mappings(()) is None


def test_builtin_resourcepack_can_be_selected_explicitly():
    layers = load_block_mappings(("resourcepack",))
    assert layers == (RESOURCEPACK,)


def test_invalid_json_mapping_is_rejected():
    with pytest.raises(BlockMappingError):
        load_block_mappings(('{"4096":"1"}',))


def test_non_string_target_is_rejected():
    with pytest.raises(BlockMappingError):
        load_block_mappings(('{"42":73}',))


def test_load_fixed_metadata_from_json_and_inline(tmp_path):
    custom = tmp_path / "custom.json"
    custom.write_text(json.dumps({"21": "35:13"}), encoding="utf-8")
    layers = load_block_mappings((str(custom), '{"85": "5:0", "21": "5"}'))
    assert layers == ({"21": "35:13"}, {"85": "5:0", "21": "5"})
    mapping = compile(layers)
    assert mapping.ids[21] == 5 and mapping.metadata[21] == 16
    assert mapping.ids[85] == 5 and mapping.metadata[85] == 0


@pytest.mark.parametrize("target", ['"35:"', '"35:16"', '"35:-1"', '"35:01"', '"035:2"', '"35:2:3"', '[35,13]', '35', 'true'])
def test_invalid_fixed_metadata_json(target):
    with pytest.raises(BlockMappingError):
        load_block_mappings((f'{{"21": {target}}}',))


def test_invalid_noncanonical_source_json():
    with pytest.raises(BlockMappingError):
        load_block_mappings(('{"0001":"5"}',))
