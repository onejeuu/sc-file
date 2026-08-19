Models
======

.. automodule:: scfile.structures.models
   :no-members:

Animation
---------

.. automodule:: scfile.structures.models.animation
   :members:
   :show-inheritance:
   :undoc-members:

Counts
------

.. automodule:: scfile.structures.models.counts
   :members:
   :show-inheritance:
   :undoc-members:

Enums
-----

.. automodule:: scfile.structures.models.enums
   :members:
   :show-inheritance:
   :undoc-members:

Features
--------

.. automodule:: scfile.structures.models.features
   :members:
   :show-inheritance:
   :undoc-members:

Matrices
--------

.. automodule:: scfile.structures.models.matrices
   :members:
   :show-inheritance:
   :undoc-members:

Mesh
----

.. automodule:: scfile.structures.models.mesh
   :members:
   :show-inheritance:
   :undoc-members:

Meta
----

.. automodule:: scfile.structures.models.meta
   :members:
   :show-inheritance:
   :undoc-members:

Scene
-----

.. automodule:: scfile.structures.models.scene
   :members:
   :show-inheritance:
   :undoc-members:

Skeleton
--------

.. automodule:: scfile.structures.models.skeleton
   :members:
   :show-inheritance:
   :undoc-members:

Transforms
----------

.. automodule:: scfile.structures.models.transforms
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: SceneTransform
   :module: scfile.structures.models.transforms

   ``Callable[[ModelScene], ModelScene]``

.. py:type:: ModelTransform
   :module: scfile.structures.models.transforms

   ``Callable[['ModelContent'], 'ModelContent']``

.. py:type:: AnimationTransform
   :module: scfile.structures.models.transforms

   ``Callable[[ModelScene, ModelScene], ModelScene]``

Types
-----

.. automodule:: scfile.structures.models.types
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: Features
   :module: scfile.structures.models.types

   ``tuple[Feature, ...]``

   Model feature collection.

.. py:type:: FeatureFlags
   :module: scfile.structures.models.types

   ``dict[Feature, bool]``

   Feature flags declared by source model.

.. py:type:: BonesMapping
   :module: scfile.structures.models.types

   ``dict[LocalBoneId, SkeletonBoneId]``

   Mapping from mesh local to skeleton bone indices.

.. py:type:: Vector2D
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 2)]``

   2D float32 vector.

.. py:type:: Vector3D
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 3)]``

   3D float32 vector.

.. py:type:: Vector4D
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 4)]``

   4D float32 vector.

.. py:type:: LinksIds
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.uint8], (..., 4)]``

   Bone indices per vertex.

.. py:type:: LinksWeights
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 4)]``

   Bone weights per vertex.

.. py:type:: Links
   :module: scfile.structures.models.types

   ``tuple[LinksIds, LinksWeights]``

   Bone indices and weights pair.

.. py:type:: Polygons
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.uint32], (..., 3)]``

   Triangle indices.

.. py:type:: BlendVertexMap
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.uint16], (...,)]``

   Blend shape base vertex index per mesh vertex.

.. py:type:: Colors
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.uint8], (..., 4)]``

   RGBA vertex colors.

.. py:type:: EulerAngles
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 3)]``

   Euler angles in degrees (XYZ intrinsic).

.. py:type:: Quaternion
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 4)]``

   Quaternion rotation (XYZW).

.. py:type:: RotationMatrix
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (3, 3)]``

   3x3 rotation matrix.

.. py:type:: TransformMatrix
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (4, 4)]``

   4×4 transformation matrix.

.. py:type:: BindPose
   :module: scfile.structures.models.types

   ``list[TransformMatrix]``

   Global transform per bone.

.. py:type:: InverseBindMatrices
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 4, 4)]``

   Inverse bind matrices per bone.

.. py:type:: AnimationTranslations
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 3)]``

   Animation translations per frame.

.. py:type:: AnimationRotations
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], (..., 4)]``

   Animation rotations per frame.

.. py:type:: AnimationTimes
   :module: scfile.structures.models.types

   ``Annotated[NDArray[np.float32], ...]``

   Animation times per frame.

.. py:type:: MorphWeights
   :module: scfile.structures.models.types

   ``NDArray[np.float32]``

   Morph channel weights per frame.
