Usage
==================================================

Use conversion functions for ordinary file conversion. Format handlers expose
the decoded content when it must be inspected, changed, or encoded manually.


Conversion
----------------------------------------

Automatic Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:func:`~scfile.convert.auto` resolves the source format from its suffix and
uses its default target format.

.. code-block:: python

  from scfile import convert

  convert.auto("model.mcsb")
  convert.auto("model.mcsb", output="path/to/output")

Without ``output``, the result is written next to the source. For automatic
conversion, ``output`` must be a directory.


Explicit Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use a named conversion function when the target format is known:

.. code-block:: python

  from scfile import Options, convert

  convert.mcsb_to_obj("model.mcsb", "model.obj")
  convert.mcsb_to_glb("model.mcsb", options=Options(skeleton=True))

The output may be an exact file name or a directory. Named conversion functions
are available from :mod:`scfile.convert`.


Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`~scfile.Options` controls parsing, conversion targets, and output
conflict handling. Skeletons and built-in animations are disabled by default.

.. code-block:: python

  from scfile import Options, convert

  options = Options(
      skeleton=True,
      animation=True,
      on_conflict="skip",
  )

  convert.mcsb_to_glb("model.mcsb", options=options)

Animation parsing also enables skeleton parsing. When skeleton processing is
enabled, automatic model conversion targets GLB by default.


External Animation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

External animation functions combine animation data with compatible models and
export GLB:

.. code-block:: python

  from scfile import convert

  convert.arms(
      "weapon.mcvd",
      weapon="weapon.mcsb",
      hands="character_hands.mcsb",
  )
  convert.face("head.mcvd", "head.mcsb")
  convert.body("character.mcal", "character.mcsb")


Handlers and Content
----------------------------------------

A decoder reads one binary format into a content object. An encoder writes a
compatible content object to another format. The content remains usable after
the decoder is closed.

.. code-block:: python

  from scfile import Options
  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb", Options(skeleton=True)) as mcsb:
      model = mcsb.decode()

  print(model.meta.version)
  print(model.scene.total_vertices)
  print([mesh.name for mesh in model.scene.meshes])
  print([bone.name for bone in model.scene.skeleton.bones])

Format handlers inherit from :class:`~scfile.core.Decoder` and
:class:`~scfile.core.Encoder`. Content types include
:class:`~scfile.structures.content.ModelContent` and
:class:`~scfile.structures.content.TextureContent`.


Manual Encoding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use an encoder directly when the conversion pipeline needs explicit control:

.. code-block:: python

  from scfile import Options
  from scfile.formats import GlbEncoder, McsbDecoder

  options = Options(skeleton=True)

  with McsbDecoder("model.mcsb", options) as mcsb:
      model = mcsb.decode()

  with GlbEncoder(model, options, output="model.glb") as glb:
      glb.encode()


Pipelines and Streams
----------------------------------------

:class:`~scfile.core.Decoder` provides two in-memory shortcuts:

* ``convert_to(Encoder)`` returns an open encoder for the decoded content.
* ``convert(Encoder)`` returns the encoded bytes.

.. code-block:: python

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      with mcsb.convert_to(ObjEncoder) as obj:
          obj.encode()
          data = obj.to_bytes()

  with McsbDecoder("model.mcsb") as mcsb:
      data = mcsb.convert(ObjEncoder)

Encoders write automatically when :meth:`~scfile.core.Encoder.save`,
:meth:`~scfile.core.Encoder.export`, or
:meth:`~scfile.core.Encoder.to_bytes` needs serialized data.

.. list-table::
  :header-rows: 1

  * - Method
    - Output path
  * - ``save("model.obj")``
    - Used as given
  * - ``export("model")``
    - ``model.obj``

Both methods close the encoder by default. Pass ``close=False`` when the
encoder must remain open.

Decoders accept paths, raw bytes, and open binary streams. Encoders use an
in-memory stream by default or accept an output path or binary stream. A
handler owns a stream passed to it, so read an external output stream before
the encoder closes.

Use a context manager whenever possible:

.. code-block:: python

  from io import BytesIO

  from scfile.formats import McsbDecoder, ObjEncoder

  output = BytesIO()

  with McsbDecoder("model.mcsb") as mcsb:
      with mcsb.convert_to(ObjEncoder, output=output) as obj:
          obj.encode()
          data = output.getvalue()

For complete signatures and data structures, see :doc:`API Reference <../scfile>`.
