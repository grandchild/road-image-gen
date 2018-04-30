import os
import sys
import bpy
import math

# To be able to find this project's modules, the path needs to be added to
# sys.path.
basepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.append(basepath)
from util.config import read_config
from blender.model import load_new_model
from blender.scenes import (
    set_resolution,
    set_depth_pixel_depth,
    link_new_scene,
    clear_scenes,
    delete_objects,
    ground_visibility,
    correct_object_names,
)
from blender.cameras import position_cameras, dump_k_matrix, setup_displacement_values
from blender.lighting import set_lighting
from grounds.meshes import cobblestone_ground, slate_ground, asphalt_ground
from grounds.meshes import always_defects
from util.output_suppressor import OutputSuppressor



VERBOSITY = 0

def main():
    '''
    Load the given config file, initialize the Blender scene and set up and
    execute rendering.
    
    Create the desired ground type, position the cameras and set up the
    lighting. Configure Blender to render both camera angles and render all
    images for one image set.
    
    By default this function loads the `config.json` file that was written out
    by the CLI, but one can also be specified as an argument when executing
    this skript directly.
    
    To directly run this script, execute (note the ``--`` before the config
    file)::
    
        $ blender --python main.py [ -- config file]
    '''
    global VERBOSITY
    basepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[3])))
    try:
        config = read_config(basepath, file=sys.argv.pop())
    except ValueError:
        config = read_config(basepath)
    VERBOSITY = config['verbose']
    vv('start, config loaded:', config)
    output_path = os.path.join(basepath, config['output'])
    
    load_new_model(os.path.join(basepath, 'model', 'base_model.blend'))
    v('model loaded')
    
    cameras = [
        bpy.data.objects['camera_left'],
        bpy.data.objects['camera_right'],
    ]
    nodes = bpy.data.scenes['main_scene'].node_tree.nodes
    
    v('generating ground meshes...')
    texture_output = os.path.join(config['output'], 'road_textures')
    if config['ground_type'] == 'cobblestone':
        cobblestone_ground(source=texture_output, size=(7,7), defects=config['defects'])
    elif config['ground_type'] == 'asphalt':
        asphalt_ground(source=texture_output, size=(7,7), defects=config['defects'])
    elif config['ground_type'] == 'slate':
        slate_ground(source=texture_output, size=(7,7), defects=config['defects'])
    else:
        raise ValueError('Unknown ground type {}'.format(config['ground_type']))
    v('ground generated')
    
    position_cameras(
        cameras,
        config['camera_distance'] / 100.0,  # cm -> m
        config['camera_pitch'],
        config['camera_inward_yaw'],
        height=config['camera_height'] / 100.0 # cm -> m
    )
    
    set_lighting()
    
    set_resolution(config['resolution'])
    
    os.makedirs(output_path, exist_ok=True)
    dump_k_matrix(cameras[0], os.path.join(output_path, 'k_matrix.csv'))
    v('K matrix written')
    
    # create a new scene and link it to a camera and render layer
    link_new_scene(
        scene_name='right',
        camera_name='camera_right',
        node_name='right'
    )
    v('left scene set up')
    
    main_scene      = bpy.data.scenes['main_scene']
    right_scene     = bpy.data.scenes['right']
    
    if config['defects'] or always_defects:
        link_new_scene(
            scene_name='defects',
            camera_name='camera_left',
            node_name='defects'
        )
        defects_scene = bpy.data.scenes['defects']
        v('defects scene set up')
    
    correct_object_names()
    
    if config['defects'] or always_defects:
        ground_visibility(main_scene, ground_visible=True, defects_visible=False)
        ground_visibility(right_scene, ground_visible=True, defects_visible=False)
        ground_visibility(defects_scene, ground_visible=False, defects_visible=True)
    
    set_depth_pixel_depth(nodes, config['depth_range'])
    # set filenames for left, depth, right & disparity pictures
    nodes['File Output'].file_slots[0].path = os.path.join(output_path, '{}-{:0>5}-#-left.png'.format(config['ground_type'], config['image_index']))
    nodes['File Output'].file_slots[1].path = os.path.join(output_path, '{}-{:0>5}-#-right.png'.format(config['ground_type'], config['image_index']))
    nodes['File Output'].file_slots[2].path = os.path.join(output_path, '{}-{:0>5}-#-depth.png'.format(config['ground_type'], config['image_index']))
    nodes['File Output'].file_slots[3].path = os.path.join(output_path, '{}-{:0>5}-#-displacement.png'.format(config['ground_type'], config['image_index']))
    nodes['File Output'].file_slots[4].path = os.path.join(output_path, '{}-{:0>5}-#-defects.png'.format(config['ground_type'], config['image_index']))
    
    factor = setup_displacement_values(nodes, cameras, 0.04)
    
    # write out images
    if VERBOSITY >= 2:
        bpy.ops.render.render(write_still=True, scene='main_scene')
    else:
        v('rendering...', end='')
        with OutputSuppressor():  # suppress render progress output
            bpy.ops.render.render(write_still=True, scene='main_scene')
        v(' done')
    # if i < config['number']-1:
    #     delete_objects()
    #     clear_scenes()
    # bpy.ops.wm.quit_blender()


def v(*msgs, end='\n'):
    '''Print messages for verbosity level 1.'''
    if VERBOSITY and VERBOSITY>= 1:
        print(*msgs, end=end, flush=True)


def vv(*msgs, end='\n'):
    '''Print messages nodes, for verbosity level 2.'''
    if VERBOSITY and VERBOSITY >= 2:
        print(*msgs, end=end, flush=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
