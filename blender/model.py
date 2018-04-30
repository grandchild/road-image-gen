import bpy


def load_new_model(model_file):
    """
    Load a model in blender

    Args:
        model_file (str): model filepath
    """
    # select and remove all objects
    for o in bpy.data.objects:
        o.select = True
    bpy.ops.object.delete()
    
    section = '\\Scene\\'
    object = 'main_scene'

    filepath = model_file + section + object
    directory = model_file + section
    filename = object

    # append main_scene from model_file
    bpy.ops.wm.append(
        filepath=filepath,
        filename=filename,
        directory=directory
    )

    #set main_scene to active scene
    bpy.context.window.screen.scene = bpy.data.scenes['main_scene']
