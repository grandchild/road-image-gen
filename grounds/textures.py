import os.path
from glob import glob
try:
    from grounds.voronoi.renderer import render as render_voronoi
except ImportError:
    print('voronoi not available')
from grounds.asphalt import generate_asphalt


depth_suffix = '_depth'
defects_suffix = '_defects'
texture_suffix = '_texture'
output_default = os.path.join('output', 'road_textures')


def cobblestone_ground_textures(defects=0, output_path=output_default):
    '''Render a new voronoi-based cobblestone image.'''
    output = os.path.join(output_path, 'cobblestone')
    os.makedirs(output_path, exist_ok=True)
    try:
        render_voronoi(
            size=10,
            grid_distortion=0.2,
            distance=0.08,
            corner_size=0.3,
            max_z_displace=130,  # of 255
            max_slant=0,  # slanted cells don't tile correctly yet
            wrap_amount=5,
            defects=defects if defects else 0,
            output=output,
            texture_images=list(glob('img/stone_textures/hrt-stone*.png')),
            background_texture='img/cobblestone_background.png',
            dpi=96*3,
        )
    except NameError:
        print('render_voronoi() not available')

def slate_ground_textures(defects=0, output_path=output_default):
    '''Render a new voronoi-based slate-stone image.'''
    output = os.path.join(output_path, 'slate')
    os.makedirs(output_path, exist_ok=True)
    try:
        render_voronoi(
            size=7,
            grid_distortion=0.5,
            distance=0.04,
            corner_size=0.3,
            max_z_displace=150,  # of 255
            max_slant=0,  # slanted cells don't tile correctly yet
            wrap_amount=5,
            defects=defects if defects else 0,
            output=output,
            texture_images=list(glob('img/stone_textures/hrt-stone*.png')),
            background_texture='img/cobblestone_background.png',
            dpi=96*3,
        )
    except NameError:
        print('render_voronoi() not available')


def asphalt_ground_textures(defects=0, output_path=output_default):
    '''Render a new asphalt noise pattern with optional defects.'''
    output = os.path.join(output_path, 'asphalt')
    os.makedirs(output_path, exist_ok=True)
    generate_asphalt(
        resolution=[1024,1024],
        asphalt_type=1,
        img_destination=output+texture_suffix+'.png',
        img_defects_destination=output+defects_suffix+'.png',
        img_depth_destination=output+depth_suffix+'.png',
        crack_length=0.8,
        number_of_cracks=defects if defects else 0,
        crack_width=10,
    )
