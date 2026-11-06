import numpy as np
import pytest

from scfile.content import RegionContent
from scfile.content.regions import ChunkSection
from scfile.core import Resources
from scfile.enums import ByteOrder
from scfile.exceptions import BlockMappingError
from scfile.formats.mca import McaEncoder, payload
from scfile.formats.mca import mappings as mca_mapping
from scfile.formats.mca.mappings import BUILTIN_MAPPINGS, RESOURCE_KEY, compile, compile_table
from scfile.io.nbt import NbtReader
from scfile.options import Options


def _decode(section: ChunkSection, mapping: np.ndarray) -> dict:
    low = mapping[:256]
    byte_mapping = low.astype(np.uint8).tobytes() if np.all(low <= 255) else None
    raw = b"\x0a\x00\x00" + payload._section(section, mapping, byte_mapping)
    with NbtReader(raw, order=ByteOrder.BIG) as reader:
        result = reader.document()
    assert isinstance(result, dict)
    return result


def test_options_normalizes_one_mapping_to_tuple():
    mapping = {42: 73}
    options = Options(block_mappings=mapping)

    assert options.block_mappings == (mapping,)
    assert isinstance(options.block_mappings, tuple)


def test_options_normalizes_none_to_empty_tuple():
    options = Options()

    assert options.block_mappings == ()


def test_mapping_layers_are_applied_in_order():
    mapping = compile_table(({5: 1, 42: 2}, {42: 73, 300: 4}, {42: 9}))

    assert mapping[5] == 1
    assert mapping[42] == 9
    assert mapping[300] == 4
    assert mapping[301] == 0
    assert not mapping.flags.writeable


def test_empty_mapping_is_a_real_air_only_layer():
    mapping = compile_table(({},))

    assert np.count_nonzero(mapping) == 0


def test_empty_layer_sequence_selects_default_mapping():
    mapping = compile_table(())

    assert mapping[7] == BUILTIN_MAPPINGS["resourcepack"][7]
    assert mapping[7] != BUILTIN_MAPPINGS["vanilla"][7]


def test_default_mapping_preserves_matching_terrain_ids():
    mapping = compile_table()

    assert mapping[1] == 1
    assert mapping[2] == 2
    assert mapping[3] == 3
    assert mapping[9] == 9
    assert mapping[11] == 11
    assert mapping[12] == 12
    assert mapping[13] == 13
    assert mapping[4025] == 0


def test_mapping_accepts_full_12_bit_source_and_target_ids():
    mapping = compile_table({4095: 4094})

    assert mapping[4095] == 4094


@pytest.mark.parametrize("layer", [{-1: 0}, {4096: 0}, {1: -1}, {1: 4096}, {True: 1}, {1: True}])
def test_mapping_rejects_invalid_ids(layer):
    with pytest.raises(BlockMappingError):
        compile_table((layer,))


def test_full_source_id_maps_to_full_target_id_and_keeps_metadata():
    blocks = memoryview(bytes([5]) * 4096)
    additions = memoryview(b"\x01" + bytes(2047))
    metadata = memoryview(b"\xa5" + bytes(2047))
    section = ChunkSection(0, blocks, metadata, additions)
    mapping = compile_table({5: 73, 261: 683})

    decoded = _decode(section, mapping)

    assert decoded["Blocks"][0] == 683 & 0xFF
    assert decoded["Blocks"][1] == 73
    assert decoded["Add"][0] & 0x0F == 683 >> 8
    assert decoded["Data"][0] == 0xA5


def test_target_high_bits_are_emitted_even_without_source_additions():
    section = ChunkSection(0, memoryview(bytes([5]) * 4096), memoryview(bytes(2048)))
    mapping = compile_table({5: 683})

    decoded = _decode(section, mapping)

    assert decoded["Blocks"][0] == 683 & 0xFF
    assert decoded["Add"][0] & 0x0F == 683 >> 8


def test_byte_translate_path_keeps_data_and_omits_empty_add():
    metadata = memoryview(b"\x34" + bytes(2047))
    section = ChunkSection(0, memoryview(bytes([5]) * 4096), metadata)
    mapping = compile_table({5: 73})

    decoded = _decode(section, mapping)

    assert decoded["Blocks"] == bytes([73]) * 4096
    assert decoded["Data"][0] == 0x34
    assert "Add" not in decoded


def test_encoder_inherits_base_constructor():
    from inspect import signature

    assert tuple(signature(McaEncoder).parameters) == ("data", "options", "output", "resources")


def test_mca_encoder_reuses_prepared_resource(monkeypatch):
    compiled = compile({5: 73})
    resources = Resources({RESOURCE_KEY: compiled})

    def unexpected_compile(*args, **kwargs):
        raise AssertionError("MCA mapping was compiled again")

    monkeypatch.setattr(mca_mapping, "compile_table", unexpected_compile)
    first = McaEncoder(RegionContent(), resources=resources)
    second = McaEncoder(RegionContent(), resources=resources)

    with first, second:
        assert first.resources is second.resources is resources
        assert first.to_bytes() == second.to_bytes()


def test_standalone_mca_encoder_compiles_only_on_encode(monkeypatch):
    original = mca_mapping.compile_table
    compiled = []

    def track(mappings=None):
        compiled.append(mappings)
        return original(mappings)

    monkeypatch.setattr(mca_mapping, "compile_table", track)
    with McaEncoder(RegionContent(), Options(block_mappings={5: 73})) as encoder:
        assert not compiled
        encoder.to_bytes()
    assert len(compiled) == 1
