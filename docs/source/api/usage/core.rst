Core Architecture
====================================

Handlers
    | Classes derived from :class:`~scfile.core.decoder.FileDecoder` and :class:`~scfile.core.encoder.FileEncoder`.
    | **Decoders** parses binary data into file content.
    | **Encoders** serializes file content into binary data.

Content
    | Classes derived from :class:`~scfile.core.content.BaseContent`.
    | File content and its structured **Data Transfer Objects** (DTO).


Resource Safety
------------------------------------
Every handler inherits from :class:`~scfile.core.base.BaseFile`, which accepts an ``IOStream`` (file paths, raw bytes, or open streams).
Because handlers hold system file or memory buffers, streams must be closed after use.

Use context manager ``with`` or ``close()`` method:

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
