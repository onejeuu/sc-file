Formats
======================

.. automodule:: scfile.formats
  :no-members:
  :show-inheritance:
  :undoc-members:

| The :mod:`scfile.formats` module offers granular control for experienced users.
| Use decoders/encoders in a context manager (`with` block) for resource safety.

Usage Patterns
-------------------

**1. Recommended Context Approach**:

.. code-block:: python
  :linenos:

  # Single-step conversion using format-specific sugar method
  with McsaDecoder("model.mcsa") as mcsa:
    mcsa.to_obj().save("output.obj")  # Сloses encoder buffer

**2. Manual Pipeline**:

.. code-block:: python
  :linenos:

  # Full control over the conversion process
  with McsaDecoder("model.mcsa") as mcsa:
    data = mcsa.decode()  # ModelContent context dataclass

  with ObjEncoder(data) as obj:
    obj.save("output.obj")  # Or encoder.getvalue() for bytes

For details on available methods, refer to :mod:`scfile.core`.

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
