
Training Images Generation for Stereoscopic Neural Networks
===========================================================

The goal of this software is to allow the easy creation of artificial
stereoscopic images of roads as would be taken from two cameras mounted onto a
car. These images can then be used to train neural networks that are able to
calculate the depth of given points on the road and thus create a 3D model of
the road in front of the car.

Additionally the goal is to allow such a neural network to discover defects in
the road, such as cracks and potholes, the images generated optionally include
random defects, along with images marking these errors, so that they might be
used for training.

The ground-truth depth data is rendered as both a *distance*- and a
*disparity* image.


.. toctree::
    :caption: Contents:
    :maxdepth: 2
    
    Home <self>
    
    manual
    
    modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
