import bpy
import re


def set_resolution(resolution, resolution_percentage=100):
    """
    Set the rendering resolution. Optionally set the resolution 
    TODO(Jakob)
    """
    if resolution_percentage:
        bpy.context.scene.render.resolution_percentage = resolution_percentage
    scale = bpy.context.scene.render.resolution_percentage
    bpy.context.scene.render.resolution_x = resolution[0] // (scale / 100)
    bpy.context.scene.render.resolution_y = resolution[1] // (scale / 100)


def set_depth_pixel_depth(nodes, depth_range='16bit'):
    '''Set the pixel sample depth for the depth images.'''
    depth = '8' if depth_range == '8bit' else '16'
    nodes['File Output'].file_slots[2].format.color_depth = depth
    nodes['File Output'].file_slots[3].format.color_depth = depth


def ground_visibility(scene, ground_visible, defects_visible):
    """
    Sets the ground visibilities in blender

    Args:
        scene (bpy.types.Scene): A scene in blender
        ground_visible (bool): If True then its visible otherwise its invisible for the render processing
        defects_visible (bool) If True then the defects ground is visible otherwise its invisible for the render processing
    """
    if scene.name == 'main_scene':
        scene.objects['ground'].hide_render = not ground_visible
        scene.objects['defects'].hide_render = not defects_visible
    else:
        # for n, _ in bpy.data.objects.items():
        #     print(n)
        scene.objects[scene.name + '_ground'].hide_render = not ground_visible
        scene.objects[scene.name + '_defects'].hide_render = not defects_visible


def delete_objects():
    """
    Deletes all blender objects
    """
    for o in bpy.data.objects:
        o.select = True
    bpy.ops.object.delete()    


def correct_object_names(scene_name=None):
    """
    Corrects the object names in blender.

    Args:
        scene_name (str): if ``None`` then it corrects the object names globally: 
                          For Example: object_name.007 => object_name
                          Otherwise it corrects the object names for the given scene name:
                          For Example: object_name.005 => scene_name + object_name
    """
    if scene_name:
        for name, object in bpy.context.scene.objects.items():
            object.name = scene_name + '_' + re.sub(r'\.\d+', '', name)
    else:
        for name, object in bpy.data.objects.items():
            object.name = re.sub(r'\.\d+', '', name)

        
def link_new_scene(scene_name, camera_name, node_name):
    """
    Links a scene to a Render Layer node in blender.

    Args:
        scene_name (str):  Name of a scene in blender
        camera_name (str): Name of a camera in blender
        node_name (str): Name of a Render Layer node in blender
    """
    #set main_scene to active scene
    bpy.context.window.screen.scene = bpy.data.scenes['main_scene']
    # create new scene with all objects from the initial scene
    bpy.ops.scene.new(type='LINK_OBJECT_DATA')
    bpy.context.window.screen.scene.name = scene_name
    # set the active camera for scene right_scene
    bpy.context.scene.camera = bpy.data.objects[camera_name]
    
    # link the compositing nodes to the new scene
    node = bpy.data.scenes['main_scene'].node_tree
    node.nodes[node_name].scene = bpy.data.scenes[scene_name]
    correct_object_names(scene_name)


def clear_scenes():
    """
    Delete all scenes whos name arent 'Scene'
    """
    for s in bpy.data.scenes:
        if not(s.name == 'Scene'):
            bpy.data.scenes.remove(s)


if __name__ == '__main__':
    correct_object_names()
