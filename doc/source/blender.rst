Blender Modules
===============

The *Blender*-related modules manipulate the blender scene before the
rendering takes place.


Scenes
^^^^^^

.. automodule:: blender.scenes
    :members:


Cameras
^^^^^^^

.. automodule:: blender.cameras
    :members:


Grounds
^^^^^^^

.. automodule:: grounds.textures
    :members:

.. automodule:: grounds.meshes
    :members:


Lighting
^^^^^^^^

In order to have a more realistic as well as randomly varied color balance
throughout the resulting images, the :py:meth:`set_lighting` function will
slightly adjust the light color and intensity for every new image. The hue of
the lighting will be chosen from either reddish or blueish tones and then
randomized slightly around the base hue. The coloring effect is always very
subtle.

.. automodule:: blender.lighting
    :members:


Model
^^^^^

.. automodule:: blender.model
    :members:

