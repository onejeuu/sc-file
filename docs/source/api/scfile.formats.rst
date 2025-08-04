Formats
======================

.. automodule:: scfile.formats
  :no-members:
  :show-inheritance:
  :undoc-members:

| This module offers granular control for experienced users.
| Refer to :mod:`scfile.core` for details on available decoder/encoder methods.

**Base Components:**

- :class:`FileDecoder <scfile.core.decoder.FileDecoder>` - read and parse files into structured data.
- :class:`FileEncoder <scfile.core.encoder.FileEncoder>` - convert structured data into file formats.
- :class:`FileContent <scfile.core.context.content.FileContent>` - intermediate data representation.

.. tip::

  Always use decoder/encoder in context manager (``with``) for resource safety.

Usage Examples
-------------------

.. code-block:: python
  :caption: Basic Conversion

  from scfile import formats
  from scfile.core import ModelContent

  # Decode MCSB model
  with formats.mcsb.McsbDecoder("model.mcsb") as mcsb:
    data: ModelContent = mcsb.decode()  # Get parsed data

  # Encode OBJ model
  with formats.obj.ObjEncoder(data) as obj:
    obj.encode()           # Write data to buffer
    obj.save("model.obj")  # Save and close encoder

.. code-block:: python
  :caption: Get encoded bytes instead of saving

  with formats.obj.ObjEncoder(data) as obj:
    # You can use encoder methods right on encode() (chaining)
    output: bytes = obj.encode().getvalue()  # Returns OBJ bytes

.. code-block:: python
  :caption: Use ``convert_to()`` method

  with formats.mcsb.McsbDecoder("model.mcsb") as mcsb:
    # No need to call mcsb.decode()
    # convert_to() creates an encoder and pass decoded data to it
    mcsb.convert_to(formats.obj.ObjEncoder).save("model.obj") # Save and close encoder

    # Or use precreated sugar methods
    mcsb.to_obj().save("model.obj") # Save and close encoder

.. code-block:: python
  :caption: Use ``encoded()`` method

  # No need to call obj.encode()
  with formats.obj.ObjEncoder(data).encoded() as obj:
    obj.save("model.obj") # Save and close encoder

Formats
------------------

.. toctree::
  :maxdepth: 2

  scfile.formats.dae
  scfile.formats.dds
  scfile.formats.glb
  scfile.formats.hdri
  scfile.formats.mcsa
  scfile.formats.mcsb
  scfile.formats.mic
  scfile.formats.ms3d
  scfile.formats.obj
  scfile.formats.ol
  scfile.formats.png
  scfile.formats.texarr
  scfile.formats.zip
