Default Pipelines
========================================

Execution Lifecycle
-------------------

Initialization of decoders and encoders only binds stream targets and settings.
Data processing occurs during explicit method calls:

* :meth:`~scfile.core.decoder.FileDecoder.decode` Parses source stream and fills data container.
* :meth:`~scfile.core.encoder.FileEncoder.encode` Serializes data container into output binary stream.


Conversion Interfaces
---------------------

Methods for direct cross-format conversion without manual instance management:

* :meth:`~scfile.core.decoder.FileDecoder.convert_to` Calls decoder and returns a new encoder instance initialized with parsed data.
* :meth:`~scfile.core.decoder.FileDecoder.convert` Decodes source, encodes it to target format, returns raw bytes, and closes streams automatically.
* Format-specific methods (e.g., ``as_obj()``) that mirror behavior (syntax sugar) of :meth:`~scfile.core.decoder.FileDecoder.convert_to`.


Examples
-----------------------

.. code-block:: python
   :caption: Basic Manual Pipeline

   from scfile.formats.mcsb import McsbDecoder
   from scfile.formats.obj import ObjEncoder

   with McsbDecoder("model.mcsb") as mcsb:
       data = mcsb.decode()

   with ObjEncoder(data) as obj:
       obj.encode().save("output.obj")

.. code-block:: python
   :caption: Chaining and Factory Shortcuts

   from scfile.formats.mcsb import McsbDecoder
   from scfile.formats.obj import ObjEncoder

   with McsbDecoder("model.mcsb") as mcsb:
       # convert_to triggers decode() internally and returns a clear encoder
       with mcsb.convert_to(ObjEncoder) as obj:
           obj.encode().save("output.obj")

       # Using explicit target format shortcuts in a concise single-line chain.
       # If encode() is omitted, the persistence layer invokes it automatically.
       mcsb.as_obj().save("output.obj")

.. code-block:: python
   :caption: High-Level Encapsulated Conversion

   from scfile.formats.mcsb import McsbDecoder
   from scfile.formats.obj import ObjEncoder

   # Standard high-level pipeline returning raw format bytes directly
   with McsbDecoder("model.mcsb") as mcsb:
       data: bytes = mcsb.convert(ObjEncoder)

   # Extracting buffer data
   with ObjEncoder(data) as obj:
       data: bytes = obj.getvalue()  # Automatically triggers encode() if buffer is empty

.. code-block:: python
    :caption: Alternative Stream Handling

    from io import BytesIO
    from scfile.formats.mcsb import McsbDecoder
    from scfile.formats.obj import ObjEncoder

    source = b"..."
    output = BytesIO()

    with McsbDecoder(source) as mcsb:
        data = mcsb.decode()

    # Directing serialization stream into specified output
    with ObjEncoder(data, output=output) as obj:
        obj.encode()
        # output now contains serialized structure

    with open("output.obj", "wb") as fp:
        fp.write(output.getvalue())




Persistence
-----------

Methods for saving encoded data to disk or retrieving buffers:

* ``save(path)`` / ``save_as(path)`` Write data strictly to the specified file path.
* ``export(path)`` / ``export_as(path)`` Append the format suffix (e.g., ``.obj``) to the path and write the data.

Methods with the ``_as`` suffix keep the encoder stream open. Standard methods
(``save``, ``export``) close the stream automatically after writing.

.. code-block:: python
   :caption: Persistence Options

   from scfile.formats.obj import ObjEncoder

   with ObjEncoder(data) as obj:
       # Appends format extension automatically
       obj.encode().export("model") # Closes stream
       assert obj.closed

   with ObjEncoder(data) as obj:
       obj.encode()

       # Keeps encoder open to duplicate data or append modifications
       obj.export_as("backup")
       assert not obj.closed

       obj.save_as("backup.obj")
       assert not obj.closed

       obj.save("model.obj") # Closes stream
       assert obj.closed
