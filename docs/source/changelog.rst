📋 Changelog
==================================================

v6.0.0
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Animations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``scfile animate``: added ``arms()``, ``face()``, and ``body()`` commands for animation export to ``.glb``.
* ``convert.arms()``: exports first-person ``.mcvd`` animation with ``.mcsb`` weapon and hands models.
* ``convert.face()``: exports facial ``.mcvd`` animation with ``.mcsb`` head model.
* ``convert.body()``: exports ``.mcal`` skeletal clips with ``.mcsb`` model.
* ``Options.preserve_clips``: keeps every decoded ``.mcal`` clip during body animation export.
* ``McvdDecoder``: standalone decoder instead of alias.
* ``mcvd_to_obj()``, ``mcvd_to_glb()``, and ``mcvd_to_fbx()``: added named ``.mcvd`` conversions.

Handlers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``McsaDecoder``: now supports blend shapes parsing.
* ``GlbEncoder``: now exports blend shapes and morph animation clips.
* ``FbxEncoder``: now exports armature and builtin bone animation clips.
* ``EfkmodelDecoder``: now parses uv2, normals, tangents.
* ``HandlerState`` and ``Handler.state``: added operation lifecycle states.
* ``ModelMeta``: added source model version, feature flags, and element counts.
* ``ModelContent.has()`` and ``ModelScene.has()``: report present model features.
* ``ModelDecoder.features`` and ``ModelEncoder.features``: declare model features supported by handlers.

Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``scfile convert --include``: filters source formats during directory conversion.
* ``scfile convert --layout``: added ``dump``, ``relative``, and ``rooted`` output layouts.
* ``scfile convert --verbose``: prints the result of every processed file.
* ``scfile.formats.registry``: now defines built-in decoders, encoders, filename aliases, and supported conversion paths.
* ``scfile mapcache --biomes/--no-biomes``: controls biome data export to ``.mca`` files.


Application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **GUI:** added animation and settings tabs.
* **GUI:** added forms for arms, face, and body animation export.
* **GUI:** added configured game directory and persistent export settings.
* **GUI:** reset output path to default on backspace if empty field.
* **Tools**: ``audit --relations``: validates animation-to-model relations for arms, face, and body assets.
* **Documentation:** added Map Cache viewing and animation export guides.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Minimum Python version raised to ``3.13``.
* ``convert.auto()`` now returns destination path on success or ``None`` on skip.
* ``scfile convert --model-format`` (``-F``): now accepts one target format.
* ``scfile convert --output``: default layout changed from flat ``dump`` to ``rooted``.
* ``TaskFeedback``: reworked with live progress, output location, and files summary.
* ``McWorld.find()``: resolves Minecraft 26.1+ ``dimensions/minecraft/overworld/region`` directories.
* **Documentation:** updated most pages.

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **GUI:** disabled controls now display the unavailable cursor.
* **Model transforms:** no longer modify source content.
* **Conversion:** sources with colliding output paths no longer overwrite each other during conversion.

🗑️ Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

File Formats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``DaeEncoder`` (``.dae``): removed output format.
* ``Ms3dEncoder`` (``.ms3d``): removed output format.
* ``ol_cubemap_to_dds()``: removed in favor of ``ol_to_dds()``.
* **API:** removed ``as_*()`` conversion methods.

CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``scfile mapcache --raw``: removed raw block ID export.
* CLI options ``--relative`` and ``--parent`` (replaced by ``--layout``).

Library API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Support of Python ``3.11`` and ``3.12``.
* ``FileEncoder.save_as()`` and ``FileEncoder.export_as()``: replaced by ``Encoder.save(close=False)`` and ``Encoder.export(close=False)``.
* ``FileDecoder.decode()``: removed ``seek`` parameter.
* ``FileDecoder.convert()``: removed ``output`` parameter.
* ``FileEncoder.getvalue()``: renamed to ``Encoder.to_bytes()``.
* ``FileEncoder.save()`` and ``FileEncoder.export()``: removed ``mode`` parameter.
* ``BaseContent.reset()``.
* ``scfile.core.types`` module.

⚡ Optimized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``scfile convert --workers``: processes files in parallel.
* ``convert.files.manual()``: writes to staged temporary files before publishing output.

♻️ Refactored
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``scfile`` entry point: moved to ``scfile.app.launcher``.
* ``scfile.cli`` and ``scfile.gui``: moved to ``scfile.app.cli`` and ``scfile.app.gui``.

Core and Content
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``BaseFile``: renamed to ``Handler``.
* ``Handler``: no longer inherits ``IOBase``. Binary stream operations moved to ``Handler.io``.
* ``StructIO``: no longer inherits ``IOBase``. Wraps a binary stream.
* ``BaseFile.ctx``: replaced by read-only ``Handler.context``.
* ``BaseFile.suffix``: replaced by ``Handler.suffix()``.
* ``FileDecoder`` and ``FileEncoder`` hook methods: renamed to protected ``_*`` methods.
* ``scfile.core.content`` and ``scfile.structures``: moved to ``scfile.content``.
* ``ModelContent.version`` and ``ModelContent.flags``: replaced by ``ModelContent.meta.version`` and ``ModelContent.meta.flags``.
* ``TexarrContent`` and ``NbtContent``: replaced by ``ArchiveContent`` and ``DocumentContent``.
* ``FileType`` and ``BaseContent.type``: renamed to ``FileKind`` and ``BaseContent.kind``.
* ``FileDecoder`` and ``FileEncoder``: renamed to ``Decoder`` and ``Encoder``.
* ``scfile.core.structio``: moved to ``scfile.io.base``.
* ``scfile.core.options``: moved to ``scfile.options``.
* ``scfile.consts`` and ``scfile.enums``: redistributed to more specific modules.
* ``Options.model_formats``: replaced by ``Options.targets``, a mapping of content types to output formats.
* ``Options.full_chunk``: renamed to ``Options.extended_chunk``.
* ``Options.on_conflict`` and ``scfile convert --on-conflict``: ``overwrite`` renamed to ``replace``.

Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``convert.convert``: renamed to ``convert.files.manual``.
* ``convert.detect``: replaced by ``convert.files.auto`` and ``convert.files.format``.
* ``convert.factory``: replaced by ``scfile.formats.registry`` and ``convert.named``.


v5.2.1 (2026-07-26)
----------------------------------------

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``FileEncoder.save()``, ``FileEncoder.export()``: close the encoder when serialization fails.



v5.2.0 (2026-07-24)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``OlDecoder``: support for ``DXN_X`` (``ATI1`` / ``BC4``) textures.
* ``TextureKind``: OL texture kind identifiers.
* ``OlKindUnsupported``: error for unsupported OL texture kinds.
* ``decoders()``, ``encoders()``: access to registered decoder and encoder classes.
* ``converter()``: source format aliases.
* ``scfile.formats``: decoder and encoder class exports.
* ``detect.format()``: input format detection by file name.
* ``TextureContent.path_hash``: logical resource path hash.
* ``SafetyLimit``: shared limits for decoded sizes and counts.
* ``LimitError``: error for decoded values that exceed a safety limit.
* **Development:** public ``audit``, ``info`` and ``profile`` tools.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``OlDecoder``: default and cubemap textures are now detected from the OL kind field.
* ``OlDecoder``: texture data is typed as ``DefaultTexture | CubemapTexture``.
* **Docs:** expanded format descriptions and library usage guide.
* **Templates:** updated binary format structures.

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: facial bones and morph animation structure in model version 15.0.
* ``DaeEncoder``: ``float_array`` counts in generated documents.
* ``OlDecoder``: invalid compressed mipmaps now report ``InvalidStructureError``.

⚠️ Deprecated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``OlCubemapDecoder``: use ``OlDecoder`` instead.
* ``ol_cubemap_to_dds()``: use ``ol_to_dds()`` instead.

🗑️ Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaCountsLimit``: replaced by ``LimitError``.

⚡ Optimized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``Ms3dEncoder``: numeric data serialization (1.2 s → 20 ms).
* ``DaeEncoder``, ``ObjEncoder``: numeric data serialization.



v5.1.1 (2026-07-01)
----------------------------------------

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Templates:** updated binary format structures.

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: parsing blend shape flag in model version 15.0.



v5.1.0 (2026-06-03)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: support for model version 15.0.
* **GUI:** sidebar navigation.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``BaseFile.location``: now returns a meaningful source identifier.
* **GUI:** redesigned color scheme and component styles.
* **GUI:** update check now caches results for 60 seconds.



v5.0.1 (2026-05-26)
----------------------------------------

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **GUI:** incorrect language detection.
* **GUI:** assets missing from the PyPI package.



v5.0.0 (2026-05-25)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GUI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Graphical interface:** implemented with ``PySide6`` and launched when no arguments are provided.
* ``ConverterTab``: drag & drop, file type filters, output structure options.
* ``MapCacheTab``: ``.mdat`` to ``.mca`` conversion.
* ``VersionWidget``: update check popup with GitHub release lookup.

CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Command structure:** ``scfile convert`` and ``scfile mapcache``.
* ``scfile.__main__``: automatically runs ``convert`` when a file or directory is given as first argument.
* ``--updates``: update check option.
* ``--on-conflict``: output conflict option (``overwrite``, ``rename``, ``skip``).
* ``params``: Click types ``Files``, ``Output``, ``MapCacheDir``, ``Formats`` and ``OnConflict``.

File Formats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``EfkmodelDecoder``: new source format ``.efkmodel`` (geometry only).
* ``McalDecoder``: new source format ``.mcal`` (animation library, no export).
* ``MdatDecoder``: new source format ``.mdat`` (region cache).
* ``McaEncoder``: new output format ``.mca`` (Anvil regions).
* ``FbxEncoder``: new output format ``.fbx`` (geometry only).
* ``nbt.nbt``: NBT encoding functions (``encode()``, ``compound()``, ``list()``, etc.).
* ``mca.mapping``: block ID mapping table for the Anvil format.

Library API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``StructIO``: unified stream class replacing ``StructBytesIO`` and ``StructFileIO``.
* ``BaseFile``: unified binary stream adapter for file paths, bytes and IO streams.
* ``FileDecoder.convert_to()``: ``output`` parameter (``IOStream``).
* ``FileEncoder.transform()`` hook and transforms pipeline.
* ``RegionContent``: world chunk container.
* ``RegionChunk``, ``ChunkHeader``: world chunk structures.
* ``ModelContent``: ``uv2``, ``tangents`` and ``colors`` fields.
* ``FileEncoder``, ``FileDecoder``: ``prelude()`` hooks.

Model Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``transforms``: scene transformation functions.
* ``ModelMesh`` fields: ``uv2``, ``tangents``, ``colors``, ``link_space``, ``uv_origin``, ``uv_sign``, ``max_influences``.
* ``ModelSkeleton`` fields: ``space``, ``hierarchy``.
* ``AnimationClip``: replaced ``transforms`` with ``rotations`` and ``translations``.
* ``SkeletonBone``: ``slug`` property.
* **Enums:** ``UVOrigin``, ``UVSign``, ``LinkSpace``, ``SkeletonSpace``, ``SkeletonHierarchy``, ``AnimationTranslation`` and ``AnimationRotation``.
* **Type aliases:** ``EulerAngles``, ``TransformMatrix``, ``BindPose``, etc.

Utilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Converter registry:** ``converters()`` and ``registry()`` functions with the ``@converter`` decorator for format pairs.
* ``scfile.utils``: new package.
* ``files``: ``resource()``, ``resolve()``, ``walk()``, ``destination()``.
* ``versions``: ``Version`` dataclass with parsing and comparison.
* ``updates``: update checking against GitHub API.
* ``regions``: region merging from scattered map cache files.
* ``cli``: callbacks ``version_callback``, ``updates_callback``.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Library API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``UserOptions``: renamed to ``Options``.
* ``UserOptions.parse_skeleton``: renamed to ``Options.skeleton``.
* ``UserOptions.parse_animation``: renamed to ``Options.animation``.
* ``UserOptions.overwrite``: replaced by ``Options.on_conflict``.
* ``FileEncoder.save_as()``, ``FileEncoder.export_as()``: now return ``Self``.

Model Formats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Model decoders:** ``to_XXX()`` methods replaced by ``as_XXX()``. They return an empty encoder; ``encode()`` must be called explicitly.
* **Model decoders:** ``prepare()`` replaced by a transforms list.
* ``GlbEncoder._add_meshes()``: writes ``uv2`` and ``tangents`` when present.
* ``DaeEncoder._add_controller_sources()``: checks ``max_influences > 0``.
* ``McsaFileIO._links()``: normalizes bone weights.

* **Constants:** ``NBT_FILENAMES`` renamed to ``SUPPORTED_NBT``.
* **Tests:** coverage 100% excluding ``scfile.gui``.

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: UV2 and tangent parsing (exported only to ``.glb``).
* ``GlbEncoder``: binary data for meshes without skinning links when a skeleton is present.

🗑️ Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **CLI:** ``--unique`` option (replaced by ``--on-conflict rename``).
* ``FileFormat.ITEMNAMES`` (replaced by ``FileFormat.NBT``).
* ``McsaBoneLinksError`` (replaced by a silent fallback).
* ``scfile.cli.commands.py``, ``scfile.cli.types.py``, ``scfile.cli.utils.py``.
* ``SceneCounts``, ``MeshCounts``.
* ``structures.types``.
* ``enums.FileMode``.

♻️ Refactored
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``core.io``: moved to ``core.structio``.
* ``core.context``: split into ``core.content`` and ``core.options``.
* ``structures.models``: now contains ``animation``, ``mesh``, ``skeleton``, ``scene``, ``flags`` and ``vectors``.
* ``consts.McsaUnits``: moved to ``formats.mcsa.consts``.
* ``consts.OlString``: moved to ``formats.ol.io``.
* ``StructBytesIO``, ``StructFileIO``: merged into ``StructIO``.
* ``convert.legacy``: merged back into ``convert.formats``.

Data Structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``AnimationClip.transforms``: split into ``rotations`` and ``translations``.
* ``ModelMesh.positions``: renamed to ``ModelMesh.vertices``.
* ``ModelMesh.textures``: renamed to ``ModelMesh.uv1``.
* ``TextureArrayContent``: renamed to ``TexarrContent``.
* ``TextureArrayDecoder``: renamed to ``TexarrDecoder``.
* ``TextureArrayEncoder``: renamed to ``TexarrEncoder``.
* ``NbtBytesIO``: renamed to ``NbtBufferIO``.
* ``McsaModel``: renamed to ``ModelDefaults``.
* ``MeshOrigin``: renamed to ``MeshBounds``.



v4.4.1 (2026-05-21)
----------------------------------------

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: incorrect polygon count after converting quads to triangles.
* ``GlbEncoder``: incorrect geometry produced from polygon quads.



v4.4.0 (2026-05-11)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: support for polygon quads in model version 12.0.

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: version-specific flag sets for model versions 7.0, 8.0 and 9.0 or newer.
* ``McsaDecoder``: polygon quads converted to triangles.



v4.3.0 (2026-03-04)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: support for model version 12.0.



v4.2.1 (2026-01-01)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* List of supported NBT files in ``--version`` output.

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Pyinstaller rich unicode bundle.



v4.2.0 (2026-01-01)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``NbtDecoder``: new source format NBT (``itemnames.dat`` and synchronized configs).
* ``JsonEncoder``: new output format ``.json``.
* **CLI:** ``--version`` output now includes an emoji.



v4.1.2 (2025-10-17)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **CLI:** usage hint when no arguments are provided.



v4.1.1 (2025-08-08)
----------------------------------------

⚡ Optimized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``ObjEncoder``: faster export (450 ms → 170 ms).



v4.1.0 (2025-08-06)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``TextureArrayDecoder``: new source format ``.texarr``.
* ``TextureArrayEncoder``: new output format ``.zip``.
* ``convert.texarr_to_zip()``: new converter.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``GlbEncoder``: uses a single bind matrix.
* ``GlbEncoder``: writes position accessor bounds.
* ``scfile.formats``: package imports improved.

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``GlbEncoder``: glTF output for meshes without skinning links when a skeleton is present.

⚡ Optimized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``StructIO``: faster array reads (``.mcsa`` parsing 53 ms → 8 ms).



v4.0.0 (2025-05-25)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``GlbEncoder``: new output format ``.glb``.
* ``McsaDecoder``, ``GlbEncoder``: skeleton parsing and export through ``--skeleton``.
* ``McsaDecoder``, ``GlbEncoder``: built-in animation parsing and export through ``--animation``.
* ``OlCubemapDecoder``: cubemap texture decoder.
* ``OlDecoder``: support for ``RGBA32F`` (DX10) textures.
* **CLI:** ``--parent`` option.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Textures:** cubemap textures fall back from default texture decoding on failure.

CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Batch conversion: unexpected errors no longer interrupt processing.
* ``--model-formats``: renamed to ``--mdlformat``.
* ``--hdri``: renamed to ``--cubemap``.
* ``--no-overwrite``: renamed to ``--unique``.
* Default model output format changed to ``.obj``.
* Default model output format with ``--skeleton`` changed to ``.glb``.

Core
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``FileDecoder.validate()``: renamed to ``FileDecoder.validate_signature()``.
* ``FileDecoder.convert_to()``, ``convert()``: ``options: UserOptions`` parameter.
* ``FileDecoder``, ``FileEncoder``: removed content reset on ``close()``.
* ``FileContent``: new property ``type: FileType``.
* ``FileFormat``: new property ``suffix: str``.

⚡ Optimized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: array reads through ``StructIO`` (model parsing 12× faster).
* **CLI:** ``files_map`` replaced by an iterator, eliminating startup delays on large directories.



v3.6.1 (2024-11-13)
----------------------------------------

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``DdsEncoder``: incorrect alpha channel mask in ``.dds`` output.



v3.6.0 (2024-09-06)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **CLI:** new command-line interface.
* ``OlDecoder``: partial support for cubemap textures (first face only).



v3.5.4 (2024-06-15)
----------------------------------------

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``ObjEncoder``: material names now included in ``.obj`` output through ``usemtl``.

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **CLI:** ``scfile`` command is now installed correctly by ``pip``.



v3.5.0 (2024-05-31)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaDecoder``: support for model version 11.0.
* ``OlDecoder``: support for all mipmap levels.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **CLI:** ``--output`` now accepts only a directory.
* ``convert.auto()``: default model export formats changed to ``.obj`` and ``.ms3d``.
* **Textures:** raw formats preserved without conversion to ``RGBA8``.
* ``McsaDecoder``: bone link parsing disabled pending output format support.

🗑️ Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Textures:** support for ``RGBA32F`` textures (used by one known asset).



v3.4.1 (2024-05-31)
----------------------------------------

🐛 Fixed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``DaeEncoder``: non-functional test skeleton removed from exported scenes.



v3.4.0 (2024-05-29)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``DaeEncoder``: new output format ``.dae`` (COLLADA).

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``FileDecoder.decode()``: file position reset to the beginning after parsing.
* ``McsaFileIO``: decoded floats rounded to six decimal places.

🗑️ Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``mcvd_to_*``: conversion functions removed because ``.mcvd`` and ``.mcsa`` use the same structure.

♻️ Refactored
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Formats:** moved to ``scfile.file.formats``.
* **Core:** base classes moved to ``scfile.file.base``.
* **Core:** data components moved to ``scfile.file.data``.
* **CLI:** entry point moved from ``scfile.__main__`` to ``scfile.cli``.
* **Models:** dataclasses reorganized.
* **Core:** general structure reorganized.



v3.3.1 (2024-05-14)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``Ms3dBinEncoder``: new output format ``.ms3d`` (MilkShape 3D Binary).
* ``Ms3dAsciiEncoder``: new output format ``.txt`` (MilkShape 3D ASCII).

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **CLI:** default export formats now include ``.obj`` and ``.txt``.
* **CLI:** implementation moved to a dedicated module.
* **Models:** model dataclasses updated.



v3.2.0 (2024-04-30)
----------------------------------------

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Core:** general code cleanup.

⚡ Optimized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``McsaFileIO``: faster model parsing.



v3.1.0 (2024-04-14)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Models:** partial support for source format ``.mcvd`` (animations unsupported).

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Core:** internal API updated.



v3.0.3 (2023-03-25)
----------------------------------------

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Models:** ``.obj`` export now uses mesh names as object groups.
* **Models:** float output precision moved to a constant.
* ``FileDecoder``: file open mode is now exposed as a property.



v3.0.0 (2024-03-20)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Models:** vertex normals parsing.
* **Textures:** support for normal map textures.
* **Textures:** conversion from ``BGRA8``, ``RGBA32F`` and ``DXN_XY`` to ``RGBA8``.
* **Tests:** initial pytest coverage.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Core:** internal API rewritten.



v2.0.0 (2023-12-20)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Models:** support for all known model versions.
* **Models:** safety limits for corrupted files to prevent excessive memory use.
* **Textures:** support for all known texture formats.
* **CLI:** multiple input files.

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Core:** internal API updated.
* **Models:** model data structures changed from ``dict`` to ``list``.
* **Models:** skeleton parsing disabled pending output format support.

⚡ Optimized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Models:** parsing up to 10× faster for common files.



v1.4.2 (2023-10-20)
----------------------------------------

📝 Changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``ObjFile``: object group renamed from ``<Root>`` to the source file name.
* ``utils.func``: renamed to ``utils.convert``.
* ``scfile.reader.enums``: reader enums moved to a dedicated module.
* **DDS:** header structure moved to ``dds_structure``.



v1.3.2 (2023-10-18)
----------------------------------------

✨ Added
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* First stable release.
