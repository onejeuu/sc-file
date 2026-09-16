from scfile.formats import registry


def test_match() -> None:
    assert registry.decoders
    for format, decoder in registry.decoders.items():
        assert registry.match(f"source{format.suffix}") is decoder
        for name in registry.aliases.get(format, ()):
            assert registry.match(name) is decoder


def test_filters() -> None:
    filters = registry.filters()
    assert filters
    for name in filters:
        decoder = registry.match(f"source{name}" if name.startswith(".") else name)
        assert decoder is not None
        assert decoder.exportable


def test_conversions() -> None:
    assert registry.conversions
    for (source, target), conversion in registry.conversions.items():
        assert conversion.decoder is registry.decoders[source]
        assert conversion.encoder is registry.encoders[target]
        assert conversion.decoder.content_type is conversion.encoder.content_type
