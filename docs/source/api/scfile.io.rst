💾 IO
==================================================

.. automodule:: scfile.io
   :no-members:

Base
----

.. automodule:: scfile.io.base
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: IOStream
   :module: scfile.io.base

   ``SourceLike | IOBase | bytes``

.. py:type:: OutputStream
   :module: scfile.io.base

   ``SourceLike | IOBase``

Fbx
---

.. automodule:: scfile.io.fbx
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: Scalar
   :module: scfile.io.fbx

   ``bool | int | float | str | bytes | np.integer | np.floating``

.. py:type:: Float32Array
   :module: scfile.io.fbx

   ``NDArray[np.float32]``

.. py:type:: Float64Array
   :module: scfile.io.fbx

   ``NDArray[np.float64]``

.. py:type:: Int32Array
   :module: scfile.io.fbx

   ``NDArray[np.int32]``

.. py:type:: Int64Array
   :module: scfile.io.fbx

   ``NDArray[np.int64]``

.. py:type:: UInt32Array
   :module: scfile.io.fbx

   ``NDArray[np.uint32]``

.. py:type:: Array
   :module: scfile.io.fbx

   ``Float32Array | Float64Array | Int32Array | Int64Array``

.. py:type:: Value
   :module: scfile.io.fbx

   ``Scalar | Array | list[Scalar]``

.. py:type:: Cluster
   :module: scfile.io.fbx

   ``tuple[Int32Array, Float64Array]``

Models
------

.. automodule:: scfile.io.models
   :members:
   :show-inheritance:
   :undoc-members:

Nbt
---

.. automodule:: scfile.io.nbt
   :members:
   :show-inheritance:
   :undoc-members:

Ol
--

.. automodule:: scfile.io.ol
   :members:
   :show-inheritance:
   :undoc-members:
