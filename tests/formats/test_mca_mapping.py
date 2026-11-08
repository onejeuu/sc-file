import numpy as np
import pytest

from scfile.content import RegionContent
from scfile.content.regions import ChunkSection, ChunkTileMaterials
from scfile.core import Resources
from scfile.enums import ByteOrder
from scfile.exceptions import BlockMappingError
from scfile.formats.mca import McaEncoder, mappings, payload
from scfile.formats.mca.mappings import CompiledBlockMapping
from scfile.io.nbt import NbtReader
from scfile.options import Options


def _decode(section: ChunkSection, mapping: CompiledBlockMapping) -> dict:
    low = mapping.ids[:256]
    byte_mapping = low.astype(np.uint8).tobytes() if np.all(low <= 255) else None
    raw = b"\x0a\x00\x00" + payload._section(section, mapping, byte_mapping)
    with NbtReader(raw, order=ByteOrder.BIG) as reader:
        result = reader.document()
    assert isinstance(result, dict)
    return result


def test_builtin_mappings_share_the_raw_dict_shape():
    assert isinstance(mappings.BUILTIN["vanilla"], dict)
    assert isinstance(mappings.BUILTIN["resourcepack"], dict)
    assert all(
        isinstance(source, str) and isinstance(target, str)
        for mapping in mappings.BUILTIN.values()
        for source, target in mapping.items()
    )


def test_vanilla_mapping_contains_the_complete_studio_mapping():
    mapping = mappings.BUILTIN["vanilla"]

    assert len(mapping) == 401
    assert mapping["12"] == "13:0"
    assert mapping["43"] == "43"
    assert mapping["4006"] == "148:0"

    compiled = mappings.compile((mapping,))
    assert compiled.ids[43] == 43
    assert compiled.ids[4006] == 148


def test_options_normalizes_one_mapping_to_tuple():
    mapping = {"42": "73"}
    options = Options(block_mappings=mapping)

    assert options.block_mappings == (mapping,)
    assert isinstance(options.block_mappings, tuple)


def test_options_normalizes_none_to_empty_tuple():
    options = Options()

    assert options.block_mappings == ()


def test_mapping_layers_are_applied_in_order():
    mapping = mappings.compile(({"5": "1", "42": "2"}, {"42": "73", "300": "4"}, {"42": "9"}))

    assert mapping.ids[5] == 1
    assert mapping.ids[42] == 9
    assert mapping.ids[300] == 4
    assert mapping.ids[301] == 0
    assert not mapping.ids.flags.writeable


def test_empty_mapping_is_a_real_air_only_layer():
    mapping = mappings.compile(({},))

    assert np.count_nonzero(mapping.ids) == 0


def test_empty_layer_sequence_selects_default_mapping():
    mapping = mappings.compile(())
    default = mappings.BUILTIN[mappings.DEFAULT]

    assert mapping.ids[7] == int(default["7"].split(":", 1)[0])


def test_default_mapping_applies_builtin_targets():
    mapping = mappings.compile()
    default = mappings.BUILTIN[mappings.DEFAULT]

    for source in ("1", "2", "3", "9", "11", "12", "13"):
        assert mapping.ids[int(source)] == int(default[source].split(":", 1)[0])
    assert mapping.ids[4025] == 0


def test_mapping_accepts_full_12_bit_source_and_target_ids():
    mapping = mappings.compile({"4095": "4094"})

    assert mapping.ids[4095] == 4094


@pytest.mark.parametrize(
    "layer", [{"-1": "0"}, {"4096": "0"}, {"1": "-1"}, {"1": "4096"}, {True: "1"}, {"1": True}, {1: "2"}]
)
def test_mapping_rejects_invalid_ids(layer):
    with pytest.raises(BlockMappingError):
        mappings.compile((layer,))


def test_full_source_id_maps_to_full_target_id_and_keeps_metadata():
    blocks = memoryview(bytes([5]) * 4096)
    additions = memoryview(b"\x01" + bytes(2047))
    metadata = memoryview(b"\xa5" + bytes(2047))
    section = ChunkSection(0, blocks, metadata, additions)
    mapping = mappings.compile({"5": "73", "261": "683"})

    decoded = _decode(section, mapping)

    assert decoded["Blocks"][0] == 683 & 0xFF
    assert decoded["Blocks"][1] == 73
    assert decoded["Add"][0] & 0x0F == 683 >> 8
    assert decoded["Data"][0] == 0xA5


def test_target_high_bits_are_emitted_even_without_source_additions():
    section = ChunkSection(0, memoryview(bytes([5]) * 4096), memoryview(bytes(2048)))
    mapping = mappings.compile({"5": "683"})

    decoded = _decode(section, mapping)

    assert decoded["Blocks"][0] == 683 & 0xFF
    assert decoded["Add"][0] & 0x0F == 683 >> 8


def test_byte_translate_path_keeps_data_and_omits_empty_add():
    metadata = memoryview(b"\x34" + bytes(2047))
    section = ChunkSection(0, memoryview(bytes([5]) * 4096), metadata)
    mapping = mappings.compile({"5": "73"})

    decoded = _decode(section, mapping)

    assert decoded["Blocks"] == bytes([73]) * 4096
    assert decoded["Data"][0] == 0x34
    assert "Add" not in decoded


def test_encoder_inherits_base_constructor():
    from inspect import signature

    assert tuple(signature(McaEncoder).parameters) == ("data", "options", "output", "resources")


def test_mca_encoder_reuses_prepared_resource(monkeypatch):
    compiled = mappings.build({"5": "73"})
    resources = Resources({mappings.RESOURCE_KEY: compiled})

    def unexpected_compile(*args, **kwargs):
        raise AssertionError("MCA mapping was compiled again")

    monkeypatch.setattr(mappings, "build", unexpected_compile)
    first = McaEncoder(RegionContent(), resources=resources)
    second = McaEncoder(RegionContent(), resources=resources)

    with first, second:
        assert first.resources is second.resources is resources
        assert first.to_bytes() == second.to_bytes()


def test_standalone_mca_encoder_compiles_only_on_encode(monkeypatch):
    original = mappings.build
    compiled = []

    def track(mappings=None):
        compiled.append(mappings)
        return original(mappings)

    monkeypatch.setattr(mappings, "build", track)
    with McaEncoder(RegionContent(), Options(block_mappings={"5": "73"})) as encoder:
        assert not compiled
        encoder.to_bytes()
    assert len(compiled) == 1


def test_fixed_metadata_and_preservation_are_compiled_together():
    mapping = mappings.compile({"21": "35:13", "85": "5", "4095": "683:0"})

    assert mapping.ids[21] == 35
    assert mapping.metadata[21] == 13
    assert mapping.ids[85] == 5
    assert mapping.metadata[85] == 16
    assert mapping.ids[4095] == 683
    assert mapping.metadata[4095] == 0
    assert not mapping.ids.flags.writeable
    assert not mapping.metadata.flags.writeable


def test_later_plain_layer_removes_fixed_metadata():
    mapping = mappings.compile(({"21": "35:13"}, {"21": "5"}))
    assert mapping.ids[21] == 5
    assert mapping.metadata[21] == 16
    assert mapping._low_metadata_mask is None


def test_later_fixed_layer_replaces_prior_fixed_metadata():
    mapping = mappings.compile(({"21": "35:13"}, {"21": "35:0"}))
    assert mapping.metadata[21] == 0


@pytest.mark.parametrize(
    "value", ["-1:0", "4096:0", "35:-1", "35:16", "35:", "35:3:2", ":3", "35:01", "035:1", "35:True", "", (35, 13), 35]
)
def test_invalid_target(value):
    with pytest.raises(BlockMappingError):
        mappings.compile({"21": value})


@pytest.mark.parametrize("source", ["-1", "4096", "01", "1:0", " 1", "", 1, True])
def test_invalid_source(source):
    with pytest.raises(BlockMappingError):
        mappings.compile({source: "35"})


def test_explicit_metadata_patches_both_nibbles_and_preserves_unrelated():
    blocks = bytes([21, 85, 85, 21]) + bytes([85]) * 4092
    metadata = b"\x42\x91" + bytes([0x3B]) * 2046
    section = ChunkSection(0, memoryview(blocks), memoryview(metadata))
    mapping = mappings.compile({"21": "35:13", "85": "5"})

    decoded = _decode(section, mapping)
    assert decoded["Blocks"][:4] == bytes([35, 5, 5, 35])
    assert decoded["Data"][:2] == bytes([0x4D, 0xD1])
    assert decoded["Data"][2:] == metadata[2:]
    assert "Add" not in decoded


def test_explicit_zero_metadata_replaces_only_relevant_nibble():
    section = ChunkSection(0, memoryview(bytes([85, 21]) * 2048), memoryview(b"\xaf" * 2048))
    mapping = mappings.compile({"21": "35:0", "85": "5"})
    decoded = _decode(section, mapping)

    assert decoded["Data"] == b"\x0f" * 2048


def test_fixed_metadata_on_high_source_id_and_high_target_id():
    blocks = memoryview(bytes([5, 21]) * 2048)
    additions = memoryview(b"\x01" + bytes(2047))
    metadata = memoryview(b"\xab" + bytes(2047))
    section = ChunkSection(0, blocks, metadata, additions)
    mapping = mappings.compile({"261": "683:4", "21": "35:13", "5": "73:7"})
    decoded = _decode(section, mapping)

    assert decoded["Blocks"][:2] == bytes([683 & 255, 35])
    assert decoded["Add"][0] == 683 >> 8
    assert decoded["Data"][0] == 0xD4
    assert decoded["Data"][1] == 0xD7


def test_byte_path_is_retained_when_fixed_metadata_source_is_absent():
    section = ChunkSection(0, memoryview(bytes([5]) * 4096), memoryview(b"\xab" * 2048))
    mapping, byte_mapping = mappings.build({"5": "73", "21": "35:13"})

    assert byte_mapping is not None
    assert mapping._low_metadata_mask is not None
    blocks, add, data = payload._mapped_blocks(section, mapping, byte_mapping)
    assert blocks == bytes([73]) * 4096
    assert add == b""
    assert data == b"\xab" * 2048


def test_high_source_metadata_override_does_not_disable_low_byte_path():
    mapping, byte_mapping = mappings.build({"5": "73", "261": "683:12"})
    assert byte_mapping is not None
    assert mapping._low_metadata_mask is None
    section = ChunkSection(0, memoryview(bytes([5]) * 4096), memoryview(b"\xab" * 2048))
    assert payload._mapped_blocks(section, mapping, byte_mapping) == (bytes([73]) * 4096, b"", b"\xab" * 2048)


def test_tile_primary_material_is_projected_before_existing_mapping():
    import struct

    section = ChunkSection(
        4,
        memoryview(bytes([0xC2]) * 4096),
        memoryview(bytes([0xAA]) * 2048),
    )
    materials = ChunkTileMaterials(
        memoryview(struct.pack(">3i", -1, 67, 16)),
        memoryview(struct.pack(">H", 0xD123)),
    )
    mapping, byte_mapping = mappings.build({"291": "35:7"})

    tile_data = payload._tile_materials_by_section(materials)
    assert tile_data is not None
    tile_y, indices, states = tile_data
    assert tile_y.tolist() == [4]
    assert indices.tolist() == [3 * 256 + 15]
    assert states.tolist() == [0xD123]

    blocks, add, data = payload._mapped_blocks(
        section,
        mapping,
        byte_mapping,
        tile_indices=indices,
        tile_states=states,
    )

    index = 3 * 256 + 15
    assert blocks[index] == 35
    assert add == b""
    assert data[index // 2] == 0x7A
    assert bytes(section.blocks) == bytes([0xC2]) * 4096
    assert bytes(section.metadata) == bytes([0xAA]) * 2048
