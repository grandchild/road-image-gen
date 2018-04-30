CLI
===

::

    usage: image_generator.py [-h] [-n NUMBER] [-r RESOLUTION] [-o OUTPUT]
                              [-g {cobblestone,asphalt,slate}] [-d DEFECTS]
                              [--camera-distance CAMERA_DISTANCE]
                              [--camera-pitch CAMERA_PITCH]
                              [--camera-inward-yaw CAMERA_INWARD_YAW] [-p PROJECT]
                              [-b BLENDERPATH] [-f] [-v] [-q]

    create stereoskopic test images for neural network training

    optional arguments:
      -h, --help            show this help message and exit
      -n NUMBER, --number NUMBER
                            number of output images (default: 1)
      -r RESOLUTION, --resolution RESOLUTION
                            [width]x[height] of the output images (default:
                            960x540)
      -o OUTPUT, --output OUTPUT
                            output path for images (will be created if non-
                            existing) (default: output)
      -g {cobblestone,asphalt,slate}, --ground-type {cobblestone,asphalt,slate}
                            ground style (default: asphalt)
      -d DEFECTS, --defects DEFECTS
                            number of road defects (default: 0)
      -D {8bit,16bit}, --depth-range {8bit,16bit}
                            depth output pixel bit depth (default: 16bit)
      --camera-distance CAMERA_DISTANCE
                            horizontal camera distance (in cm) (default: 20.0)
      --camera-pitch CAMERA_PITCH
                            camera pitch downward (in deg) (default: 12.5)
      --camera-height CAMERA_HEIGHT
                            vertical camera distance (in cm) (default: 125.0)
      --camera-inward-yaw CAMERA_INWARD_YAW
                            camera rotation towards each other (in deg, 0° to 15°
                            makes sense, depending on --camera-distance) (default:
                            0.0)
      -p PROJECT, --project PROJECT
                            path to project directory (default:
                            /home/jakob/doc/uni/mt-
                            projekt/Code/blender/image_generator)
      -b BLENDERPATH, --blenderpath BLENDERPATH
                            path to blender executable (default: blender)
      -f, --foreground      show blender UI (default: False)
      -v, --verbose         increase output verbosity level (default: 0)
      -q, --quiet           don't print any output (default: False)
