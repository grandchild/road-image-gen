import bpy
from random import uniform, choice
from colorsys import hls_to_rgb, ONE_SIXTH, TWO_THIRD

def set_lighting():
    """
    Sets the lighting for our 3d World in blender
    """
    luminence = 0.5
    saturation = 0.1
    lamp_name = 'Lamp1'
    haziness = 4
    set_haziness(haziness, lamp_name)
    set_lamp_color(luminence, saturation, lamp_name)


def set_object(object_name):
    """
    Returns a blender object

    Args:
        object_name (str): blender object name

    Returns:
        (blender object): Object in Blender like  a plane, square etc 
    """
    return bpy.data.objects[object_name]

def set_lamp_color(luminence, saturation, lamp_name):
    """
    Sets the color for our lamp in the blender 3D World.

    Args:
        luminence (float): TODO(Jakob)
        saturation (float): TODO(Jakoc)
        lamp_name (str): blender lamp name
    """
    hue = uniform(ONE_SIXTH-0.05, ONE_SIXTH+0.05) + choice([0, 0.5])  # something yellow-ish or blue-ish
    color = hls_to_rgb(hue, luminence, saturation)
    lamp = set_object(lamp_name)
    lamp.data.color = color



def set_haziness(haziness, lamp_name):
    """
    Sets the haziness for the blender lamp

    Args:
        haziness (int): Haziness for the blender lamp
        lamp_name (str): blender lamp name
    """
    lamp = set_object(lamp_name)
    lamp.data.sky.atmosphere_turbidity = haziness

def set_sun_properties(sun_brightness, sun_size, lamp_name):
    """
    Sets some properties for the blender lamp.

    Args:
        sun_brightness (float): brightness for the blender lamp sun
        sun_size (float): size for the blender sun
        lamp_name (str): blender lamp name
    """
    lamp = set_object(lamp_name)
    lamp.data.sky.sun_brightness = sun_brightness
    lamp.data.sky.sun_size = sun_size


if __name__ == '__main__':
    set_lighting()
