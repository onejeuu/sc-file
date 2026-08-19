🛠️ Core
==================================================

.. automodule:: scfile.core
   :no-members:

Base
----

.. automodule:: scfile.core.base
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: HandlerContext
   :module: scfile.core.base

   ``dict[str, Any]``

   Format-specific values retained for diagnostics.

Decoder
-------

.. automodule:: scfile.core.decoder
   :members:
   :show-inheritance:
   :undoc-members:

Encoder
-------

.. automodule:: scfile.core.encoder
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: ContentTransform
   :module: scfile.core.encoder

   ``Callable[[ContentType], ContentType]``

   Function that transforms content before serialization.

.. py:type:: EncoderTransforms
   :module: scfile.core.encoder

   ``Sequence[ContentTransform[ContentType]]``

   Ordered content transforms applied by an encoder.

Models
------

.. automodule:: scfile.core.models
   :members:
   :show-inheritance:
   :undoc-members:
