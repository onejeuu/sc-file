Core Architecture
====================================

Data and Logic Separation
-------------------------
The library separates file processing logic from data containers.

Processors
    Classes derived from :class:`~scfile.core.decoder.FileDecoder` and :class:`~scfile.core.encoder.FileEncoder`.
    **Decoders** parse binary data into structured objects.
    **Encoders** serialize these objects into binary format.

Containers
    Classes derived from :class:`~scfile.core.content.BaseContent`.
    They are dataclasses that act as **Data Transfer Objects** (DTO).
    Containers hold file kind representation in memory and expose its fields for reading and modification.


Resource Safety
------------------------------------
Every processor inherits from :class:`~scfile.core.base.BaseFile`, which accepts
an ``IOStream`` (file paths, raw bytes, or open streams). Because processors
hold system file handles or memory buffers, streams must be closed after use.

Resource disposal can be handled automatically via a context manager or manually using the ``close()`` method:

.. code-block:: python
  :caption: Example

  from scfile.formats.mcsb import McsbDecoder

  # Option 1: Automatic cleanup via context manager (preferred)
  with McsbDecoder("model.mcsb") as mcsb:
      content = mcsb.decode()

  # Entering the context opens the stream.
  # Exiting guarantees that underlying file descriptor or memory buffer is closed.

  # Option 2: Manual cleanup via close()
  mcsb = McsbDecoder("model.mcsb")
  try:
      content = mcsb.decode()
  finally:
      mcsb.close()  # Flushes data, detaches stream, and releases the handle
