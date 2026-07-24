Default Pipelines
==================================================

* :meth:`~scfile.core.decoder.FileDecoder.convert_to` decodes content and returns an encoder.
* :meth:`~scfile.core.decoder.FileDecoder.convert` decodes and encodes content, then returns the result as bytes.
* Format-specific methods such as ``as_obj()`` are shortcuts for :meth:`~scfile.core.decoder.FileDecoder.convert_to`.


Examples
----------------------------------------

.. code-block:: python
  :caption: Manual Pipeline

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      content = mcsb.decode()

  with ObjEncoder(content) as obj:
      obj.encode().save("output.obj")

.. code-block:: python
  :caption: Encoder Factory

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      with mcsb.convert_to(ObjEncoder) as obj:
          obj.save("output.obj")

      mcsb.as_obj().save("output.obj")

.. code-block:: python
  :caption: Encoded Bytes

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      data = mcsb.convert(ObjEncoder)

.. code-block:: python
  :caption: Binary Streams

  from io import BytesIO

  from scfile.formats import McsbDecoder, ObjEncoder

  source = b"..."
  output = BytesIO()

  with McsbDecoder(source) as mcsb:
      with mcsb.convert_to(ObjEncoder, output=output) as obj:
          obj.encode()
          data = output.getvalue()


Persistence
----------------------------------------

Methods for writing encoded data:

* ``save(path)`` and ``save_as(path)`` write to the specified file path.
* ``export(path)`` and ``export_as(path)`` append the format suffix to the path.

Methods with the ``_as`` suffix keep the encoder open. ``save()`` and ``export()`` close it.
All four methods encode the content automatically when the output stream is empty.

.. code-block:: python
  :caption: Persistence

  from scfile.formats import ObjEncoder

  with ObjEncoder(content) as obj:
      obj.export("model")
      assert obj.closed

  with ObjEncoder(content) as obj:
      obj.export_as("backup")
      assert not obj.closed

      obj.save_as("backup.obj")
      assert not obj.closed

      obj.save("model.obj")
      assert obj.closed
