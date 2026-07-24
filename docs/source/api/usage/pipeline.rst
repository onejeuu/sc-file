Pipelines
==================================================

Handlers can be composed directly when content must be inspected, changed, or kept in memory.


Manual Pipeline
----------------------------------------

Decoding and encoding are separate operations:

.. code-block:: python

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      model = mcsb.decode()

  with ObjEncoder(model) as obj:
      obj.save("model.obj")

``save()`` encodes automatically because the encoder stream is empty.
Call ``encode()`` explicitly when serialization must happen before persistence.


Shortcuts
----------------------------------------

:class:`~scfile.core.decoder.FileDecoder` provides three levels of shorthand:

* ``convert_to(ObjEncoder)`` decodes and returns an encoder without encoding it.
* ``as_obj()`` is the format-specific form of ``convert_to()``.
* ``convert(ObjEncoder)`` decodes, encodes, and returns ``bytes``.

.. code-block:: python

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      mcsb.as_obj().save("model.obj")

  with McsbDecoder("model.mcsb") as mcsb:
      with mcsb.convert_to(ObjEncoder) as obj:
          obj.export("model")

  with McsbDecoder("model.mcsb") as mcsb:
      data = mcsb.convert(ObjEncoder)

These methods do not close the decoder.
Its lifecycle is still controlled by its context manager.


Persistence
----------------------------------------

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
An encoder represents one serialization; do not call ``encode()`` repeatedly to duplicate its output.


Binary Streams
----------------------------------------

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

Read an external output stream before the encoder closes, because the encoder owns that stream.
