User Manual
===========


Installation
^^^^^^^^^^^^

You need to install `Blender`_, any recent version will do.

The following python packages are needed as well:

    * ``pillow``
    * ``cairosvg``
    * ``pyclipper``
    * ``pyvoronoi``

``pyvoronoi`` is tough to install on Windows but the last three, including
``pyvoronoi`` are only needed when rendering `cobblestone` and `slate`
grounds. `asphalt` needs the ``pillow`` module.

.. _Blender:
    https://www.blender.org/download/

Quickstart
^^^^^^^^^^

To simply generate one image set, run the following from within the project
directory::

    $ ./image_generator.py --defects 3

On Windows and OSX you will probably need to announce the Blender location as
well:

.. code-block:: text

    C:> image_generator.py --blenderpath "C:\Program Files\Blender\blender.exe" --defects 3

or something to that effect.

This will generate 5 images inside the `output` directory in the project
directory, like this:

    * `output/asphalt-00000-0-left.png`
    * `output/asphalt-00000-0-right.png`

These two are the camera images, in 24bit RGB, to be used as the input to the training.

    * `output/asphalt-00000-0-depth.png`
    * `output/asphalt-00000-0-displacement.png`

These two contain the ground truth output data: The distance from the camera,
and the pixel displacement between the two cameras respectively. The reference
camera is in both cases the left camera. The depth image is from the left
perspective, and the displacement shows how far the right image pixels are
from their corresponding left pixels.

Two CSV files with tables for mapping pixel values to distances in meter for
each depth and displacement are generated dynamically as well.

And finally,

    * `output/asphalt-00000-0-defects.png`

contains a black-or-white marker image indicating where road defects are in
the original image, so that the neural net may also learn to identify these
kind of defects. (Only if ``-d`` | ``--defects`` is set and `>0`)

Camera
^^^^^^

A K-Matrix defining the Blender cameras is written as a CSV file to the
`output` directory as well. More parameters can be set via the CLI, see below.

Roads
^^^^^

.. sidebar:: Road types
    
    .. image:: _static/asphalt_sample.png
    
    Asphalt detail
    
    .. image:: _static/cobblestone_sample.png
    
    Cobblestone detail


There are three types of road, which you can select from with the
``-g`` | ``--ground-type`` parameter.

    * ``asphalt``
    * ``cobblestone``
    * ``slate``

`Asphalt` roads feature cracks, and `Cobblestone` and `Slate`
surfaces feature missing stones.



Tweaking Parameters
^^^^^^^^^^^^^^^^^^^

A few things to configure:

``-n`` | ``--number``
    The number of image sets to generate. Since a single image set will take
    from about one minute up to three minutes to generate, the script will run
    for a while to generate a sizeable training set that can be used for
    neural networks. Generating thousands of images is possible, given a day
    or two.

``--camera-pitch``, ``--camera-inward-yaw``, ``--camera-distance``, ``--camera-height``
    Set up the kind of camera to use. `pitch` and `inward-yaw` set the camera
    rotations, while `distance` defines the distance of the cameras from each
    other, and `height` sets the height of both cameras from the ground.
    Rotations are given in `degree`, and distances in `cm`.

``-r`` | ``--resolution``
    The pixel dimensions of the output images. Supply a `width`x`height`
    value, e.g. ``640x480`` or ``1920x1080``. The default is a quarter HD,
    i.e. ``960x540``.

``-D`` | ``--depth-range``
    The pixel sample depth of the depth images. Can be one of ``16bit`` (the
    default) or ``8bit``.


Troubleshooting
^^^^^^^^^^^^^^^

"`Cannot locate Blender...`" error
++++++++++++++++++++++++++++++++++

Make sure that blender is installed and that the ``--blenderpath`` parameter
does indeed point to the blender executable (not just, say, the folder).
