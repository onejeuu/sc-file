Conversion
==================================================

The shortest way to use the library is :mod:`scfile.convert`.
It selects handlers, manages their streams, and writes the result.


Automatic Conversion
----------------------------------------

:func:`~scfile.convert.detect.auto` detects the source format from the file name and uses the default output format.

.. code-block:: python

  from scfile import convert

  convert.auto("model.mcsb")
  convert.auto("model.mcsb", output="path/to/output")

When ``output`` is omitted, the result is written alongside the source.
For automatic conversion, ``output`` must be a directory.


Named Conversion
----------------------------------------

Use a named function when both formats are known:

.. code-block:: python

  from scfile import convert

  convert.mcsb_to_obj("model.mcsb", "model.obj")
  convert.ol_to_dds("texture.ol", "path/to/output")

The output may be an exact file name or a directory.


Options
----------------------------------------

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
