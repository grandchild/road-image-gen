import bpy
import math
import csv


def position_cameras(cameras, distance=None, pitch=None, inward_yaw=None, height=None):
    '''
    Apply basic positioning for two stereoscopic cameras. If any of the
    arguments is None, the property will not be changed.
    If position is set, then distance needs to be set as well.
    
    Args:
        cameras (list[bpy.types.Camera]): is a 2-tuple of blender camera objects 
        height (float): should be a value in meters or None
        distance (float): should be a value in meters or None
        pitch (float): should be values in degrees or None
        inward_yaw (float): should be values in degrees or None
    '''
    cl = cameras[0]
    cr = cameras[1]
    if height:
        cl.location.y = height
        cr.location.y = height
    if distance:
        center = (cl.location.z + cr.location.z) / 2.0
        cl.location.z = center + distance / 2.0
        cr.location.z = center - distance / 2.0
    if pitch:
        cl.rotation_euler[0] = (-pitch / 180.0) * math.pi
        cr.rotation_euler[0] = (-pitch / 180.0) * math.pi
    if inward_yaw:
        cl.rotation_euler[1] = ((90.0 - inward_yaw) / 180.0) * math.pi
        cr.rotation_euler[1] = ((90.0 + inward_yaw) / 180.0) * math.pi


def dump_k_matrix(camera, filename):
    '''
    Write a 4x4 matrix containing the projection matrix for a camera into a CSV file.
    
    Args:
       camera (bpy.types.Camera): blender camera object
       filename (str): CSV filepath  

    '''
    scale = bpy.context.scene.render.resolution_percentage
    w = bpy.context.scene.render.resolution_x * (scale / 100.0)
    h = bpy.context.scene.render.resolution_y * (scale / 100.0)
    k_matrix = camera.calc_matrix_camera(w, h)
    with open(filename, 'w', newline='') as k_matrix_file:
        writer = csv.writer(k_matrix_file)
        writer.writerows(k_matrix)


def setup_displacement_values(nodes, cameras, adjustment):
    '''
    Calculate and return the factor with which to multiply the displacement image pixel values.

    Args:
        nodes (list[bpy.types.Node]): nodes contains the blender nodes
        cameras (list[bpy.types.Camera]):  
    '''
    focal_length = cameras[0].data.lens  # focal length
    camera_distance = get_cameras_distance(cameras)
    displacement_factor = adjustment * camera_distance * focal_length
    nodes['Math'].inputs[0].default_value = displacement_factor
    return displacement_factor


def get_cameras_distance(cameras):
    '''
    Return the distance between the left and right cameras.
    
    Args:
        cameras ([bpy.types.Camera, bpy.types.Camera]): is a 2-tuple of blender camera objects

    Returns:
        (float): distance between the left and right cameras
    '''
    return (cameras[0].location - cameras[1].location).length


def _depth_to_displacement(image_path, camera_distance, output_name, output_path):
    '''
    ## This function doesn't work correctly and is no longer in use! ##
    
    image_path is a path to a grayscale image containg depth information.
    camera_distance is in cm.
    
    >>> current_frame = bpy.data.scenes['main_scene'].frame_current
    >>> picName = 'depthPic-{}'.format(0) +'-'+str(current_frame)+'.png'
    >>> outputName = "Disp"+picName
    >>> depth_to_displacement(os.path.join(path, picName), camera_distance,outputName, os.path.join(path, outputName))
    '''
    import PIL
    from PIL import Image, ImageMath
    
    img = Image.open(image_path)
    r = ImageMath.eval('((({fac} * {distance}) / (i+1)) / 65536) % 256'.format(fac=256, distance=camera_distance), i=img)
    g = ImageMath.eval('((({fac} * {distance}) / (i+1)) / 256) % 256'.format(fac=256, distance=camera_distance),   i=img)
    b = ImageMath.eval(' (({fac} * {distance}) / (i+1)) % 256'.format(fac=256, distance=camera_distance),          i=img)
    newImg = Image.merge('RGB', (r, g, b))
    newImg.save(output_path)
