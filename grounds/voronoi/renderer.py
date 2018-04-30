from os import path
from cairosvg import svg2png
from .voronoi import (
    grid,
    wrap,
    distort,
    offset,
    z_displace,
    voronoi_polygons,
    slant_random,
    remove_random_cells,
    apply_random_texture,
    JOIN_SQUARE,
)
from .svg import svg_voronoi, write


def render(
        size=10,
        grid_distortion=0.5,
        distance=0.1,
        corner_size=0.3,
        foreground='white',
        background='black',
        max_z_displace=20,
        max_slant=50,
        wrap_amount=4,
        depth_suffix='_depth',
        defects=1,
        defects_suffix='_defects',
        texture_images=[],
        background_texture='',
        texture_suffix='_texture',
        dpi=96,
        output='voronoi',
        output_svg=None,
        debug_cell_center=False,
    ):
    '''
    Renders various versions of voronoi graphs as SVG or PNG images. Three
    types of images are generated: *depth*, *defects* and *texture*:
    
        * *Depth* images can be used to extrude a 3D model.
        * *Defect* images are white where stones are missing, black otherwise.
        * *Textured* images can be used to overlay a texture onto the cells, \
            depending on the list of textures provided.
    
    Args:
        size (int): The edge length of the voronoi source grid. The image will
            have size² cells. Cells might be split along the edge.
        grid_distortion (float): Distort the grid points by a certain random
            amount in x and y. The amount is relative to the cell distance. A
            distortion value of 1.0 will displace the cell at maximum one whole
            grid position.
        distance (float): The distance between cells, relative to the average
            cell size.
        corner_size (float): The corner cutoff size, relative to the average
            cell size.
        foreground (str): The color of maximum height in the depth image. Can
            be any `color string understood by SVG`_.
        background (str): The color of least height in the depth image.
        max_z_displace (float): Cells will receive a random z-coordinate up to
            this value.
        max_slant (float): Cells will get randomly slanted in z-direction up
            to this value. Use small values (start with something around
            0.01), and note that slanted cells are not wrapped properly.
        wrap_amount (int): Amount of grid points to add on two sides of the
            grid. Voronoi graphs taper off at the edges with open cells. This
            allows to create tiling images, by recreating constellations on
            the other side of the graph. Use 3 or 4 to be fairly safe. It
            might make sense to increase this further when using
            `grid_distortion` values higher than 1.
        depth_suffix (str): File name suffix to append to the output name for
            the depth image.
        defects (int): Amount of cells to remove randomly. Some effort is made
            so that only visible cells are removed, when using `wrap_amount`.
        defects_suffix (str): File name suffix to append to the output name
            for the defects image.
        texture_images (list[str]): Textures to use at random for the cells.
            If empty or ``None`` no texture image will be written.
        background_texture (str): Image file to be used as a background
            texture between cells.
        texture_suffix (str): File name suffix to append to the output name
            for the texture image.
        dpi (int): Image resolution.
        output (str): PNG output filename (without ".png" extension!). If
            empty or ``None`` no PNG images will be written.
        output_svg (str): SVG output filename (without ".svg" extension!).
            If empty or ``None`` no vector images will be written.
        debug_cell_center (bool): Render red dots at the center of cells for
            debugging the voronoi graph.
    
    .. _color string understood by SVG:
        https://www.w3.org/TR/SVG/types.html#DataTypeColor
    '''
    scale = 1000
    if wrap_amount > size:
        raise ValueError('Cannot wrap ({}) more than the grid size ({}).'.format(wrap_amount, size))
    g = grid((size, size), scale=scale)
    distort(g, (size,)*2, grid_distortion * scale)
    if max_z_displace > 0:
        z_displace(g, max_z_displace)
    if wrap_amount > 0:
        wrap(g, (size,)*2, wrap_amount, scale)
    cells = voronoi_polygons(g)
    
    
    if defects > 0:
        defect_cells = remove_random_cells(cells, defects, (size,)*2, wrap_amount, scale)
        offset(defect_cells, -distance * 0.5 * scale)
    else:
        defect_cells = []
    
    if texture_images:
        texture_cells = apply_random_texture(cells, texture_images, (size,)*2, scale)
        offset(texture_cells, -(distance + corner_size) * 0.5 * scale)
        offset(texture_cells, corner_size * 0.5 * scale, JOIN_SQUARE)
    
    offset(cells, -(distance + corner_size) * 0.5 * scale)
    if corner_size:
        offset(cells, corner_size * 0.5 * scale, JOIN_SQUARE)  # never use JOIN_ROUND, the resulting SVGs are hundreds of MB in size
    if max_slant:
        slant_random(cells, max_slant)
    svg_kwargs = {
        'size': (size,)*2,
        'scale': scale,
        'offset': (wrap_amount // 2 * scale,)*2,
        'dpi': dpi,
        'foreground': foreground,
        'background': background,
        'render_center': debug_cell_center
    }
    svg_string = svg_voronoi(cells, **svg_kwargs)
    defects_svg_string = svg_voronoi(defect_cells, **svg_kwargs)
    if texture_images:
        svg_kwargs['background'] = {
            'file': path.abspath(background_texture),
            'transform': '',
        }
        texture_svg_string = svg_voronoi(texture_cells, **svg_kwargs)
    if output:
        svg2png(bytestring=svg_string, write_to=output+depth_suffix+'.png', dpi=dpi)
        ### TODO: figure out how to get pixel data (PIL image or something similar)
        ### https://github.com/Kozea/CairoSVG/blob/master/cairosvg/__init__.py#L49
        svg2png(bytestring=defects_svg_string, write_to=output+defects_suffix+'.png', dpi=dpi)
        if texture_images:
            svg2png(bytestring=texture_svg_string, write_to=output+texture_suffix+'.png', dpi=dpi)
    if output_svg:
        write(output_svg+depth_suffix+'.svg', svg_string)
        write(output_svg+defects_suffix+'.svg', defects_svg_string)
        if texture_images:
            write(output_svg+texture_suffix+'.svg', texture_svg_string)
