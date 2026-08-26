Usage
==================================================

Conversion
----------------------------------------

Automatic Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:func:`~scfile.convert.files.auto` resolves the source format from its suffix
and uses its default target format.

.. code-block:: python

  from scfile import convert

  convert.auto("model.mcsb")
  convert.auto("model.mcsb", output="path/to/output")

Without ``output``, the result is saved alongside the source.


Explicit Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use a named conversion from :mod:`~scfile.convert.formats`
when the target format is known:

.. code-block:: python

  from scfile import convert

  convert.mcsb_to_obj("model.mcsb", output="model.obj")
  convert.mcsb_to_glb("model.mcsb", output="path/to/output")

The output may be an exact file name or a directory.


Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`~scfile.options.Options` configures conversion behavior.

.. code-block:: python

  from scfile import Options, convert
  from scfile.enums import OnConflict

  options = Options(
      skeleton=True,
      animation=True,
      on_conflict=OnConflict.SKIP,
  )

  convert.mcsb_to_glb("model.mcsb", options=options)

| By default, model conversion uses ``obj``.
| With ``skeleton`` or ``animation``, it uses ``glb``.


Animations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| :mod:`~scfile.convert.animate` exports external animations as ``.glb`` files.
| The output may be an exact file name or a directory.
| See :doc:`Animation Export guide <../../usage/animate>`.

.. code-block:: python

  from scfile import convert

  convert.arms(
      "weapon.mcvd",
      weapon="weapon.mcsb",
      hands="hands.mcsb",
  )
  convert.face("head.mcvd", "head.mcsb")
  convert.body("body.mcal", "body.mcsb")


Map Cache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| :mod:`~scfile.convert.mapcache` scans ``.mdat`` files, groups them by region, and merges them into ``.mca`` files.
| See the :doc:`Map Cache guide <../../usage/mapcache>`.


Handlers
----------------------------------------

| :class:`~scfile.core.decoder.Decoder` parses binary data into content.
| :class:`~scfile.core.encoder.Encoder` serializes content into binary data.
| :class:`~scfile.content.base.BaseContent` subclasses describe intermediate content structures.

.. code-block:: python

  from scfile import Options
  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb", Options(skeleton=True)) as mcsb:
      model = mcsb.decode()

  print(model.meta.version)
  print(model.scene.total_vertices)
  print([mesh.name for mesh in model.scene.meshes])
  print([bone.name for bone in model.scene.skeleton.bones])

Manual Encoding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use an encoder directly when conversion needs explicit control over content:

.. code-block:: python

  from scfile import Options
  from scfile.formats import GlbEncoder, McsbDecoder

  options = Options(skeleton=True)

  with McsbDecoder("model.mcsb", options) as mcsb:
      model = mcsb.decode()

  with GlbEncoder(model, options, output="model.glb") as glb:
      glb.encode()


Pipelines
----------------------------------------

:class:`~scfile.core.decoder.Decoder` provides two in-memory shortcuts:

* :meth:`~scfile.core.decoder.Decoder.convert_to` returns an open encoder.
* :meth:`~scfile.core.decoder.Decoder.convert` returns encoded bytes.

.. code-block:: python

  from scfile.formats import McsbDecoder, ObjEncoder

  with McsbDecoder("model.mcsb") as mcsb:
      with mcsb.convert_to(ObjEncoder) as obj:
          obj.encode()
          data = obj.to_bytes()

  with McsbDecoder("model.mcsb") as mcsb:
      data = mcsb.convert(ObjEncoder)


Streams
----------------------------------------

The encoder serializes its content when :meth:`~scfile.core.encoder.Encoder.save`,
:meth:`~scfile.core.encoder.Encoder.export`, or
:meth:`~scfile.core.encoder.Encoder.to_bytes` is called.

.. list-table::
  :header-rows: 1

  * - Method
    - Result
    - Closes by default
  * - ``save("model.obj")``
    - Writes to ``model.obj``
    - Yes
  * - ``export("model")``
    - Writes to ``model.obj``
    - Yes
  * - ``to_bytes()``
    - Returns encoded bytes
    - No

Decoders accept file paths, bytes, and open binary streams.
Encoders use an in-memory stream by default or accept a file path or binary stream.
Closing a handler closes its stream.

Use a context manager whenever possible:

.. code-block:: python

  from io import BytesIO

  from scfile.formats import McsbDecoder, ObjEncoder

  output = BytesIO()

  with McsbDecoder("model.mcsb") as mcsb:
      with mcsb.convert_to(ObjEncoder, output=output) as obj:
          obj.encode()
          data = output.getvalue()

For complete signatures and data structures, see :doc:`API Reference <../scfile>`.
