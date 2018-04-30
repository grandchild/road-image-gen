import os.path
import bpy


depth_suffix = '_depth'
defects_suffix = '_defects'
texture_suffix = '_texture'
output_default = os.path.join('output', 'road_textures')
always_defects = True  # override skipping defects


def cobblestone_ground(source=output_default, size=(6,6), defects=0):
    '''Load the cobblestone images as a depth mesh.'''
    source = os.path.join(source, 'cobblestone')
    mesh = _add_depth_mesh_from_image(source+depth_suffix+'.png', strength=0.03, offset=1, size=size)
    _set_texture(source+texture_suffix+'.png', mesh)
    
    if defects or always_defects:
        defects_mesh = _add_textured_mesh_from_image(source+defects_suffix+'.png', name='defects', size=size)
        _subdivide(defects_mesh)
        _add_ground_distortion(defects_mesh, noise = False)
        defects_mesh.hide_render = True

def slate_ground(source=output_default, size=(6,6), defects=0):
    '''Load the slate images as a depth mesh.'''
    source = os.path.join(source, 'slate')
    mesh = _add_depth_mesh_from_image(source+depth_suffix+'.png', strength=0.04, offset=1, size=size)
    _set_texture(source+texture_suffix+'.png', mesh)
    
    if defects or always_defects:
        defects_mesh = _add_textured_mesh_from_image(source+defects_suffix+'.png', name='defects', size=size)
        _subdivide(defects_mesh)
        _add_ground_distortion(defects_mesh, noise = False)
        defects_mesh.hide_render = True

def asphalt_ground(source=output_default, size=(6,6), defects=0):
    '''Load the asphalt images as depth mesh.'''
    source = os.path.join(source, 'asphalt')
    mesh = _add_depth_mesh_from_image(source+depth_suffix+'.png', strength=0.01, offset=1, size=size)
    _set_texture(source+texture_suffix+'.png', mesh)
    
    if defects or always_defects:
        defects_mesh = _add_textured_mesh_from_image(source+defects_suffix+'.png', name='defects', size=size)
        _subdivide(defects_mesh)
        _add_ground_distortion(defects_mesh, noise = False)
        defects_mesh.hide_render = True

def _subdivide(plane):
    # select the ground plane and enter edit mode
    bpy.context.scene.objects.active = plane

    bpy.ops.object.mode_set(mode='EDIT')
    # subdivide the mesh
    bpy.ops.mesh.subdivide(number_cuts=40)
    bpy.ops.mesh.subdivide(number_cuts=34)
    # leave edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

def _add_ground_distortion(plane, clouds=True, noise=True, strengthClouds=1, strengthNoise=0.005):
    '''
    Add two additional displacements to the ground plane. The cloud
    displacement adds a displacement modifier to create a smooth and
    extensively displacement in respect to simulate a nature terrain. The
    noise displacement can be used to create a more natural-looking surface.
    
    Args:
        plane (bpy.types.Mesh): ground plane to be modified
        clouds (bool): add cloud displacement to ground plane
        noise (bool): add noise displacement to ground plane
        strengthClouds (float): value to assign the strength of the cloud displacement
        strengthNoise (float): value to assign the strength of the noise displacement
    '''
    if clouds:
        # add new displace modifier
        mod = plane.modifiers.new(name='GROUNDDISPLACE', type='DISPLACE')
        
        # create new texture with cloud template
        if 'Clouds' not in list(bpy.data.textures.keys()):
            bpy.ops.texture.new()
            bpy.data.textures['Texture'].name = 'Clouds'
            bpy.data.textures['Clouds'].type = 'CLOUDS'
            bpy.data.textures['Clouds'].noise_depth = 0.2
            bpy.data.textures['Clouds'].noise_scale = 12
        
        mod.texture = bpy.data.textures['Clouds']
        mod.strength = strengthClouds
        mod.mid_level = 0.5
        mod.texture_coords = 'GLOBAL'
        
        # apply modifier
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='GROUNDDISPLACE')
    
    if noise:
        # add new displace modifier
        mod = plane.modifiers.new(name='GROUNDNOISE', type='DISPLACE')
        bpy.ops.texture.new()
        bpy.data.textures['Texture'].name = 'Noise'
        bpy.data.textures['Noise'].type = 'NOISE'
        mod.texture = bpy.data.textures['Noise']
        # modifier offset
        mod.mid_level = 0
        # modifier strenght/intensity
        mod.strength = strengthNoise
        # apply modifier
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='GROUNDNOISE')
        # delete texture after using, not needed anymore
        bpy.data.textures.remove(bpy.data.textures['Noise'])

def _add_depth_mesh_from_image(texture_path, strength=0.1, name='ground', offset=1, size=(6,6)):
    # add a ground plane and name it
    bpy.ops.mesh.primitive_plane_add(radius=size[0], location=(0, size[0]-1, 0))
    bpy.data.objects['Plane'].name = name
    plane = bpy.data.objects[name]
    
    _subdivide(plane)
    
    _add_ground_distortion(plane)
    _set_texture(texture_path, plane)
    
    # add new displace modifier
    mod = plane.modifiers.new(name='TEXMOD', type='DISPLACE')
    mod.texture = bpy.data.textures['plane_texture']
    mod.mid_level = offset
    mod.strength = strength
    mod.texture_coords = 'GLOBAL'
    
    # apply modifier
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier='TEXMOD')
    
    # don't use image as actual texture
    plane.data.materials[0].use_textures[1] = False
    
    # smooth object
    bpy.ops.object.shade_smooth()
    
    return bpy.data.objects[name]


def _add_textured_mesh_from_image(texture_path, name='ground_image', size=(6,6)):
    # add a ground plane and name it
    bpy.ops.mesh.primitive_plane_add(radius=size[0], location=(0, size[0]-1, 0))
    bpy.data.objects['Plane'].name = name
    _set_texture(texture_path, bpy.data.objects[name])
    return bpy.data.objects[name]


def _set_texture(texture_path, object):
    # Select object
    bpy.context.scene.objects.active = object
    # Set new object material
    object.data.materials.clear()
    newMaterial = bpy.data.materials.new('MyMaterial')
    object.data.materials.append(newMaterial)
    bpy.context.object.active_material_index = 0
    # Create new texture from image & 
    plane_texture = bpy.data.textures.new('plane_texture', type='IMAGE')
    plane_texture.image = bpy.data.images.load(texture_path)
    plane_material_texture = object.data.materials[0].texture_slots.add()
    plane_material_texture.texture = plane_texture
    # Use global texture coordinates
    plane_material_texture.texture_coords = 'GLOBAL'

