Usage
==================================================

The library can be used at several levels.
Start with conversion functions, then move to handlers and manual pipelines when more control is needed.


Conversion
----------------------------------------

The shortest way to use the library is :mod:`scfile.convert`.
It selects handlers, manages their streams, and writes the result.


Automatic Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:func:`~scfile.convert.detect.auto` detects the source format from the file name and uses the default output format.

.. code-block:: python

  from scfile import convert

  convert.auto("model.mcsb")
  convert.auto("model.mcsb", output="path/to/output")

When ``output`` is omitted, the result is written alongside the source.
For automatic conversion, ``output`` must be a directory.


Named Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use a named function when both formats are known:

.. code-block:: python

  from scfile import convert

  convert.mcsb_to_obj("model.mcsb", "model.obj")
  convert.ol_to_dds("texture.ol", "path/to/output")

The output may be an exact file name or a directory.


Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`~scfile.core.options.Options` controls work shared by converters and handlers.
Skeletons and animations are disabled by default because they require additional parsing.

.. code-block:: python

  from scfile import Options, convert

  options = Options(
      skeleton=True,
      animation=True,
      on_conflict="skip",
  )

  convert.mcsb_to_glb("model.mcsb", options=options)

Animation parsing requires skeleton parsing.


Handlers
----------------------------------------

High-level conversion is built from three independent parts:

.. code-block:: text

  source → decoder → content → encoder → output

A decoder reads one binary format into content.
An encoder writes compatible content into another binary format.
Content is the shared representation between them.
This separation lets content be inspected, changed, or encoded independently of its source.

Format handlers inherit from :class:`~scfile.core.decoder.FileDecoder` or
:class:`~scfile.core.encoder.FileEncoder`.
Handlers for individual formats are available directly from :mod:`scfile.formats`.

.. code-block:: python

  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb") as mcsb:
      content = mcsb.decode()

:meth:`~scfile.core.decoder.FileDecoder.decode` returns a content DTO such as
:class:`~scfile.core.content.ModelContent` or :class:`~scfile.core.content.TextureContent`.


Content
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Content is a hierarchy of dataclasses. Model data also uses NumPy arrays.
It remains usable after the decoder is closed.

.. code-block:: python

  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb") as mcsb:
      model = mcsb.decode()

  print(model.version)
  print(model.scene.total_vertices)
  print([mesh.name for mesh in model.scene.meshes])


Resource Safety
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A handler should be treated like a normal Python file returned by ``open()``:
it wraps an open stream, has a current position, and must be closed.
It exposes the familiar ``read()``, ``write()``, ``seek()``, ``tell()``, and ``close()`` operations.

Creating a handler from a path opens the file immediately.
Raw bytes are wrapped in an in-memory stream.
Passing an existing binary stream transfers its ownership to the handler, which closes the stream when it closes.

Use a context manager (the ``with`` statement) whenever possible:

.. code-block:: python

  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb") as mcsb:
      model = mcsb.decode()

  assert mcsb.closed

Without a context manager, call ``close()`` in ``finally`` just as with an ordinary file.


Pipelines
----------------------------------------

Handlers can be composed directly when content must be inspected, changed, or kept in memory.


Manual Pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoding and encoding are separate operations:

.. code-block:: python

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      model = mcsb.decode()

  with ObjEncoder(model) as obj:
      obj.save("model.obj")

.. note::

  | ``save()`` encodes automatically because the encoder stream is empty.
  | Call ``encode()`` explicitly when serialization must happen before persistence.


Shortcuts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`~scfile.core.decoder.FileDecoder` provides syntactic sugar:

* ``convert_to(ObjEncoder)`` decodes and returns an encoder without encoding it.
* ``convert(ObjEncoder)`` decodes, encodes, and returns ``bytes``.
* ``as_obj()`` is the format-specific form of ``convert_to()``.

.. code-block:: python

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      with mcsb.convert_to(ObjEncoder) as obj:
          obj.export_as("model")

  with McsbDecoder("model.mcsb") as mcsb:
      data = mcsb.convert(ObjEncoder)

  with McsbDecoder("model.mcsb") as mcsb:
      with mcsb.as_obj() as obj:
          obj.save_as("model.obj")

.. note::

  | Wrap encoders returned by ``convert_to()`` and ``as_*()`` in a context manager.
  | This ensures they close if a later operation fails.


Persistence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Encoder persistence methods differ in file naming and ownership:

.. list-table::
  :header-rows: 1

  * - Method
    - Output path
    - Encoder
  * - ``save("model.obj")``
    - Used as given
    - Closed
  * - ``save_as("model.obj")``
    - Used as given
    - Kept open
  * - ``export("model")``
    - ``model.obj``
    - Closed
  * - ``export_as("model")``
    - ``model.obj``
    - Kept open

All four methods encode automatically when the encoder stream is empty.
The ``_as`` variants are useful for writing the same encoded data more than once.
An encoder represents one serialization.


Binary Streams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Decoders accept paths, raw bytes, and open binary streams.
Encoders use an in-memory stream by default or accept an output stream explicitly.

.. code-block:: python

  from io import BytesIO
  from pathlib import Path

  from scfile.formats import McsbDecoder, ObjEncoder

  source = Path("model.mcsb").read_bytes()
  output = BytesIO()

  with McsbDecoder(source) as mcsb:
      with mcsb.convert_to(ObjEncoder, output=output) as obj:
          obj.encode()
          data = output.getvalue()

.. warning::

  In this case, the encoder owns the external output stream.
  Read it before the encoder closes.

For complete method signatures and available modules, see :doc:`API Reference <../scfile>`.
