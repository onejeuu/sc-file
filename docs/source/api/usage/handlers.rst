Handlers
==================================================

High-level conversion is built from three independent parts:

.. code-block:: text

  source → decoder → content → encoder → output

A decoder reads one binary format into content.
An encoder writes compatible content into another binary format.
Content is the shared representation between them.
This separation allows decoded content to be inspected or passed to any compatible encoder without reading the source again.


Handlers
----------------------------------------

Format handlers inherit from :class:`~scfile.core.decoder.FileDecoder` or
:class:`~scfile.core.encoder.FileEncoder`.
The commonly used handlers are available directly from :mod:`scfile.formats`.

.. code-block:: python

  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb") as mcsb:
      content = mcsb.decode()

A decoder does not return format-specific wrapper objects.
It returns a content DTO such as :class:`~scfile.core.content.ModelContent` or
:class:`~scfile.core.content.TextureContent`.


Content
----------------------------------------

Content contains ordinary Python objects and NumPy arrays that may be inspected or changed before encoding.
It remains usable after the decoder is closed.

.. code-block:: python

  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb") as mcsb:
      model = mcsb.decode()

  print(model.version)
  print(model.scene.total_vertices)
  print([mesh.name for mesh in model.scene.meshes])


Resource Safety
----------------------------------------

A handler should be treated like a normal Python file returned by ``open()``:
it wraps an open stream, has a current position, and must be closed.
It exposes the familiar ``read()``, ``write()``, ``seek()``, ``tell()``, and ``close()`` operations.

Creating a handler from a path opens the file immediately.
Raw bytes are wrapped in an in-memory stream.
Passing an existing binary stream transfers its ownership to the handler, which closes the stream when it closes.

Use a context manager whenever possible:

.. code-block:: python

  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb") as mcsb:
      model = mcsb.decode()

  assert mcsb.closed

Without a context manager, call ``close()`` in ``finally`` just as with an ordinary file.
