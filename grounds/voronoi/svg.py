from random import randint


def svg_voronoi(cells, size=(100, 100), scale=1.0, offset=(0, 0), foreground='black', background=None, dpi=96, render_center=False):
    '''
    Create an SVG document from the voronoi 'cells' given.
    
    Args:
        cells (list[cell]): The voronoi graph.
        size ([int, int]): The image will be `size[0]` cm x `size[1]` cm with
            the given x,y-`offset`.
        scale (float): The internal scaling factor used while creating the
            voronoi graph.
        offset ((int, int)): Upper left corner of the image. When creating
            a tiling image with a wrapped grid it should be half the wrap
            amount in each dimension.
        foreground (str): The color to be used for cells with maximum
            z-height. Intermediate values will be interpolated between
            background and foreground.
        background (str): A CSS color string setting the color of the lines
            between the cells. If ``None`` then the background will be
            transparent.
        dpi (int): Pixel density of the image. While this, along with `size`,
            does change the image dimensions, this is only needed for
            pixel-perfect tile-ability of the image. If you don't intend to
            tile the image this can be left on default.
        render_center (bool): If ``True`` the image will include little red
            dots, marking the original center point that spawned each cell,
            which can be useful for debugging.
    '''
    img_size = _fix_image_size(size, dpi)
    size = (size[0] * scale, size[1] * scale)
    svg_header = '<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'no\'?>\n\n'
    svg_header += '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    svg_header += 'width="{img_size[0]}" height="{img_size[1]}" viewBox="{offset[0]} {offset[1]} {size[0]} {size[1]}" id="pyvoronoi-display" class="pyvoronoi">\n'.format(img_size=img_size, size=size, offset=offset)
    svg_defs = '<defs>\n'
    svg_body = ''
    if background:
        if type(background) == dict:
            svg_defs += _svg_texture('tex-background', background, img_size, scale, dpi)
            background = 'url(#tex-background)'
        svg_body += '<rect x="{offset[0]}" y="{offset[1]}" width="{size[0]}" height="{size[1]}" fill="{bg}"/>\n'.format(
            offset=offset,
            size=size,
            bg=background
        )
    for i, cell in enumerate(cells):
        if len(cell.polygon) == 0:
            continue
        fill = foreground
        if cell.texture:
            texture_name = 'tex{}'.format(i)
            svg_defs += _svg_texture(texture_name, cell.texture, img_size, scale, dpi)
            fill = 'url(#{})'.format(texture_name)
        elif not cell.is_slanted:
            z = cell.center[2]
            if cell.color:
                fill = cell.color
            else:
                fill = _offset_color(foreground, z)
        else:
            gradient_stop_vector = _cell_z_bounds(cell, normalize_xy=True)
            colors = [
                _offset_color(foreground, gradient_stop_vector[0][2]),
                _offset_color(foreground, gradient_stop_vector[1][2]),
            ]
            gradient_name = 'grad{}'.format(i)
            svg_defs += _svg_gradient(
                gradient_name,
                gradient_stop_vector,
                colors
            ) + '\n'
            fill = 'url(#{})'.format(gradient_name)
        svg_body += _svg_poly(cell, fill, render_center)
    svg = svg_header + svg_defs + '</defs>\n' + svg_body + '</svg>';
    return svg

def _svg_poly(cell, fill='black', render_center=True):
    '''
    Create an SVG string describing a the polygon that describes the given
    `cell`.
    '''
    poly = ''
    try:
        poly_path = ' L '.join([
            '{},{}'.format(p[0], p[1])
            for p in cell.polygon
        ])
        poly = '<path fill="{fill}" d="M {start[0]},{start[1]} {poly} Z"/>\n'.format(
            start=cell.polygon[0],
            poly=poly_path,
            fill=fill
        )
    except IndexError:
        pass
    if render_center:
        poly += '<circle fill="#f00" stroke="none" cx="{center[0]}" cy="{center[1]}" r="70" />\n'.format(
            center=cell.center
        )
    return poly


def _svg_text(pos, text):
    '''Render a short text at the position. Used for debugging.'''
    return '<text x="{}" y="{}" fill="red" font-size="500">{}</text>\n'.format(pos.x, pos.y, text)

def _cell_z_bounds(cell, normalize_xy=False):
    '''
    Return the two points of the cell's polygon with the highest and lowest
    z-value respectively.
    
    If `normalize_xy` is ``True`` the 
    '''
    min_p = cell.polygon[0]
    max_p = cell.polygon[0]
    for p in cell.polygon[1:]:
        if min_p[2] > p[2]:
            min_p = p
        if max_p[2] < p[2]:
            max_p = p
    if normalize_xy:
        min_x = min(min_p[0], max_p[0])
        max_x = max(min_p[0], max_p[0])
        min_y = min(min_p[1], max_p[1])
        max_y = max(min_p[1], max_p[1])
        range_x = max_x - min_x
        range_y = max_y - min_y
        if range_x != 0:
            min_p = ((min_p[0] - min_x) / range_x, min_p[1], min_p[2])
            max_p = ((max_p[0] - min_x) / range_x, max_p[1], max_p[2])
        else:
            min_p = (0.5, min_p[1], min_p[2])
            max_p = (0.5, max_p[1], max_p[2])
        if range_y != 0:
            min_p = (min_p[0], (min_p[1] - min_y) / range_y, min_p[2])
            max_p = (max_p[0], (max_p[1] - min_y) / range_y, max_p[2])
        else:
            min_p = (min_p[0], 0.5, min_p[2])
            max_p = (max_p[0], 0.5, max_p[2])
    return [min_p, max_p]


def _svg_gradient(name, stop_vector, colors):
    gradient = '<linearGradient id="{name}" x1="{stops[0][0]}" y1="{stops[0][1]}" x2="{stops[1][0]}" y2="{stops[1][1]}">\n'.format(name=name, stops=stop_vector)
    for i, color in enumerate(colors):
        gradient += '\t<stop offset="{:.2}" stop-color="{}" />\n'.format(i / (len(colors) - 1), color)
    gradient += '</linearGradient>'
    return gradient


def _offset_color(foreground, z):
    z = max(0, min(255, int(z)))
    if foreground in ['white', '#ffffff', '#fff']:
        return '#{0:0>2x}{0:0>2x}{0:0>2x}'.format(255 - z)
    elif foreground in ['black', '#000000', '#000']:
        return '#{0:0>2x}{0:0>2x}{0:0>2x}'.format(z)


def _svg_texture(name, texture, img_size, scale, dpi):
    '''
    Create an SVG pattern with the given `texture` image file. Quite a bit of
    magic is involved in order to reduce spurious gaps when wrapping the
    texture. Cairos :py:meth:`svg2png` function doesn't support `<pattern>` s
    with a ``patternContentUnits="objectBoundingBox"`` very well.
    '''
    if texture is None:
        return ''
    # svg_texture = '<pattern id="{name}" patternUnits="userSpaceOnUse" width="100" height="100" patternTransform="{transform}">\n'.format(name=name, transform=texture['transform'])
    # svg_texture += '\t<image xlink:href="{file}" x="0" y="0" width="100" height="100"/>\n'.format(file=texture['file'])
    
    svg_texture = '<pattern id="{name}" '
    # svg_texture += 'width="100%" height="100%" '
    svg_texture += 'width="{w}" height="{h}" '
    # svg_texture += 'width="90" height="90" '
    # svg_texture += 'x="10" y="10" '
    # svg_texture += 'viewBox="0 0 100 100" '
    svg_texture += 'preserveAspectRatio="xMidYMid slice" '
    svg_texture += 'patternUnits="userSpaceOnUse" '
    svg_texture += 'patternContentUnits="objectBoundingBox" '
    svg_texture += 'patternTransform="{transform}" '
    svg_texture += '>\n'
    
    svg_texture += '\t<image xlink:href="{file}" '
    svg_texture += 'width="{w}" height="{h}" '
    # svg_texture += 'preserveAspectRatio="xMidYMid slice" '
    svg_texture += '/>\n'
    
    svg_texture += '</pattern>\n'
    
    ppcm = dpi/(91.44/36)
    magic = [scale-3]*2
    from PIL import Image
    img = Image.open(texture['file'])
    magic = [(s-1)*scale/dpi for s in img.size]
    img.close()
    
    svg_texture = svg_texture.format(name=name, file=texture['file'], transform=texture['transform'], w=magic[0], h=magic[1])
    # svg_texture = svg_texture.format(name=name, file=texture['file'], transform=texture['transform'], w=int(img_size[0]//3//100*100), h=int(img_size[1]//3//100*100))
    return svg_texture


def write(filename, svg):
    '''Write the SVG string to the given file.'''
    with open(filename, 'w') as f:
        f.write(svg)


def _fix_image_size(size, dpi):
    '''
    Returns the image size at the given dpi as size[0]cm by size[1]cm in pixels.
    
    This function is needed because there is a pixel missing on the lower and
    the right edge, which impedes tiling.
    
    The conversion factor for DPI->PPCM of 1/(91.44/36) comes from 91.44
    (yard to centimeter) and 36 inches per yard
    https://en.wikipedia.org/wiki/Yard
    '''
    ppcm = dpi/(91.44/36)  # 'pixels_per_centimeter'
    half_pixel_fix = 0.5
    return (size[0] * ppcm) + half_pixel_fix, (size[1] * ppcm) + half_pixel_fix
