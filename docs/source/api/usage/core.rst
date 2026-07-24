Core Architecture
==================================================

Handlers
    | Classes derived from :class:`~scfile.core.decoder.FileDecoder` and :class:`~scfile.core.encoder.FileEncoder`.
    | Decoders parse binary data into content.
    | Encoders serialize content into binary data.

Content
    | Classes derived from :class:`~scfile.core.content.BaseContent`.
    | Content and its structured Data Transfer Objects (DTO).


Resource Safety
----------------------------------------

Every handler inherits from :class:`~scfile.core.base.BaseFile`, which accepts file paths, raw bytes, and open binary streams.
Path-backed streams are opened during handler construction. Every handler owns its stream and must be closed after use.

Use a context manager or call ``close()`` explicitly:

.. code-block:: python
  :caption: Example

  from scfile.formats.mcsb import McsbDecoder

  # Automatic cleanup
  with McsbDecoder("model.mcsb") as mcsb:
      content = mcsb.decode()

  assert mcsb.closed

  # Manual cleanup
  mcsb = McsbDecoder("model.mcsb")
  try:
      content = mcsb.decode()
  finally:
      mcsb.close()
