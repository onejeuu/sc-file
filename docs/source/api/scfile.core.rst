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

.. py:type:: EncoderTransforms
   :module: scfile.core.encoder

   ``Sequence[ContentTransform[ContentType]]``

Models
------

.. automodule:: scfile.core.models
   :members:
   :show-inheritance:
   :undoc-members:
