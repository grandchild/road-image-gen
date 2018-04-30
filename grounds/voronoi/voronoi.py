'''
Create 2D Voronoi polygon meshes. Various manipulation operations are provided
as well.

This module needs the `pyvoronoi`_ and `pyclipper`_ modules to be installed.

>>> size = 3, 3
>>> grid = grid(size)
>>> distort(grid, size, 0.1, seed=0)  # `seed` is just used here to make the tests reproducible.
>>> cells = voronoi_polygons(grid)
>>> cells
[Cell(center=Point3d(0.9953193908304712, 1.0166764078910062, 0), polygon=[Point3d(1.4551020408163264, 0.5151020408163265, 0), Point3d(1.4793298969072166, 0.5393298969072164, 0), Point3d(1.532945566286216, 1.4597322212467077, 0), Point3d(0.5481618887015177, 1.5492580101180438, 0), Point3d(0.46117155624635714, 1.4604740625607149, 0), Point3d(0.516506303915063, 0.5382282680822827, 0), Point3d(0.5917915690866511, 0.46529566744730677, 0)]), Cell(center=Point3d(1.081622577039067, 2.000937371163478, 0), polygon=[Point3d(1.532945566286216, 1.4597322212467077, 0), Point3d(1.6252379693283976, 1.5423558963511368, 0), Point3d(0.2692875647668394, 16.608471502590675, 0), Point3d(0.5481618887015177, 1.5492580101180438, 0)])]
>>> offset(cells, -.1)
>>> cells
[Cell(center=Point3d(0.9953193908304712, 1.0166764078910062, 0), polygon=[Point3d(1.3833428085781634, 0.611128366086632, 0), Point3d(1.4274852615781128, 1.368907148949802, 0), Point3d(0.5863744993694127, 1.445371763780713, 0), Point3d(0.5636491654440761, 1.422177866101265, 0), Point3d(0.6139991628006101, 0.5830112439580262, 0), Point3d(0.6298481663689017, 0.5676575214602053, 0), Point3d(1.3833428085781634, 0.611128366086632, 0)]), Cell(center=Point3d(1.081622577039067, 2.000937371163478, 0), polygon=[Point3d(1.5211413651704788, 1.5833828025497496, 0), Point3d(0.4212273331359029, 13.80464982194826, 0), Point3d(0.6464850720949471, 1.640731911174953, 0), Point3d(1.4986649029888213, 1.5632610176689923, 0), Point3d(1.5211413651704788, 1.5833828025497496, 0)])]

.. _pyvoronoi:
    https://github.com/Voxel8/pyvoronoi
.. _pyclipper:
    https://github.com/greginvm/pyclipper
'''
import itertools
import random
import math as m
from copy import deepcopy
from os import path

import pyvoronoi as pv
import pyclipper as clip

from util.point import Point2d, Point3d

JOIN_SQUARE, JOIN_ROUND, JOIN_MITER = (clip.JT_SQUARE, clip.JT_ROUND, clip.JT_MITER)


def grid(size, offset=(0, 0), scale=1.0):
    '''
    Generates a regular 2D grid in 3D coordinates, with z = 0.
    
    Args:
        size (tuple[int, int]): Height and width.
        offset (tuple[int, int]): X and Y offset (Default: (0, 0)).
        scale (float): The coordinate scaling factor (Default: 1.0).
    
    >>> grid((2,2))
    [Point3d(0, 0, 0), Point3d(0, 1, 0), Point3d(1, 0, 0), Point3d(1, 1, 0)]
    
    >>> grid((3,3), (-1,-1), 2.0)
    [Point3d(-2, -2, 0), Point3d(-2, 0, 0), Point3d(-2, 2, 0), Point3d(0, -2, 0), Point3d(0, 0, 0), Point3d(0, 2, 0), Point3d(2, -2, 0), Point3d(2, 0, 0), Point3d(2, 2, 0)]
    >>> len(grid((24, 24)))
    576
    '''
    g = list(itertools.product(
        [(c + offset[0]) * scale for c in range(0, size[0])],
        [(c + offset[1]) * scale for c in range(0, size[1])]
    ))
    return [Point3d(*p, 0) for p in g]


def random_2d(size, scale=1.0, seed=None):
    '''
    Generates a size[0]*size[1]-length array with [-.5 - 0.5) valued tuples.
    
    >>> random_2d((2,2), 1.5, seed=0)
    [Point2d(0.5166327772875722, 0.3869316044104537), Point2d(-0.1191426287537325, -0.361624874560555), Point2d(0.01691208205291278, -0.14259879382437857), Point2d(0.42569788355215893, -0.2950309108816088)]
    '''
    points = []
    random.seed(seed)
    for p in range(int(size[0] * size[1])):
        points.append(Point2d((random.random() - 0.5) * scale, (random.random() - 0.5) * scale))
    return points


def distort(grid, size, scale=1.0, seed=None):
    '''
    Distorts a grid by at most `scale` in each x and y.
    
    >>> size = 2, 2
    >>> g = grid(size)
    >>> distort(g, size, 0.5, seed=0)
    >>> g
    [Point3d(0.3444218515250481, 0.2579544029403025, 0), Point3d(-0.079428419169155, 0.7589167502929633, 0), Point3d(1.0112747213686086, -0.09506586254958571, 0), Point3d(1.2837985890347725, 0.8033127260789275, 0)]
    '''
    distortion = random_2d(size, scale*2, seed=seed)
    for i, p in enumerate(grid):
        grid[i] = p + distortion[i]


def z_displace(grid, scale=1.0, seed=None):
    '''
    Randomly add a value from 0 to `scale` to the z coordinate of each point
    in `grid`.
    
    >>> g = grid((2, 2), scale=2)
    >>> z_displace(g, scale=2, seed=0)
    >>> g
    [Point3d(0, 0, 1.6888437030500962), Point3d(0, 2, 1.515908805880605), Point3d(2, 0, 0.84114316166169), Point3d(2, 2, 0.5178335005859267)]
    '''
    displacements = []
    random.seed(seed)
    for i, p in enumerate(grid):
        grid[i] = p + Point3d(z=random.random() * scale)


def wrap(grid, size, amount, scale=1.0):
    '''
    Wrap some of the upper-left points to the lower right.
    An `amount` of 1 will transform a given 3x2 grid like this::
    
        . . .      . . . .
        . . .  ->  . . . .
                   . . . .
    
    This is useful for making voronoi graphs that one can tile. Wrapping by an
    `amount` of 3 to 4, depending on the degree of added
    :py:meth:`distort`-ion, will pretty much guarantee that the resulting
    graph has matching cells along the edges created by the overlap. Then it's
    a matter of correctly cropping the image to create matching tiles. (This
    is done by the :py:meth:`grounds.voronoi.svg.svg_voronoi` method.)
    
    >>> size = 3, 2
    >>> scale = 5
    >>> g = grid(size, (1, 1), scale=scale)
    >>> g
    [Point3d(5, 5, 0), Point3d(5, 10, 0), Point3d(10, 5, 0), Point3d(10, 10, 0), Point3d(15, 5, 0), Point3d(15, 10, 0)]
    >>> wrap(g, size, 1, scale)
    [Point3d(5, 5, 0), Point3d(5, 10, 0), Point3d(10, 5, 0), Point3d(10, 10, 0), Point3d(15, 5, 0), Point3d(15, 10, 0), Point3d(20, 5, 0), Point3d(20, 10, 0), Point3d(5, 15, 0), Point3d(10, 15, 0), Point3d(15, 15, 0), Point3d(20, 15, 0)]
    '''
    for y in range(size[1]):
        for x in range(amount):
            grid.append(
                grid[x*size[1] + y] + Point3d(x=size[0]*scale)
            )
    for y in range(amount):
        for x in range(size[0]):
            grid.append(
                grid[x*size[1] + y] + Point3d(y=size[1]*scale)
            )
    for y in range(amount):
        for x in range(amount):
            grid.append(
                grid[x*size[1] + y] + Point3d(x=size[0]*scale, y=size[1]*scale)
            )
    return grid


def _add_3d_points(p1, p2):
    '''Component-wise point addition'''
    return (p1[0] + p2[0], p1[1] + p2[1], p1[2] + p2[2])


class Cell:
    '''
    Represents a Voronoi graph cell.
    
    Args:
        center (Point3d): origin point of the voronoi cell.
        polygon (list[Point3d]): cell shape.
    '''
    def __init__(self, center, polygon, is_slanted=False, index=None, color=None, texture=None):
        self.center = center
        self.polygon = polygon
        self.is_slanted = is_slanted
        self.index = index
        self.color = color
        self.texture = texture
    
    def __deepcopy__(self, _):
        return Cell(*[deepcopy(a) for a in [
            self.center, self.polygon, self.is_slanted, self.index, self.color, self.texture
        ]])
    
    def __repr__(self):
        return 'Cell(center={!r}, polygon={!r})'.format(self.center, self.polygon)


def voronoi_polygons(grid):
    '''
    Creates Voronoi polygons in x,y from a set of points.
    
    Returns:
        cell (list[Cell]): the cells of the graph. A cell has a `center` and a\
            `polygon` list of vertices. An example can be seen below:
    
    >>> g = grid((3, 3), scale=2.5)
    >>> voronoi_polygons(g)
    [Cell(center=Point3d(2.5, 2.5, 0), polygon=[Point3d(3.75, 1.25, 0), Point3d(3.75, 3.75, 0), Point3d(1.25, 3.75, 0), Point3d(1.25, 1.25, 0)])]
    '''
    pyvoronoi_scaling = 100.0
    voro = pv.Pyvoronoi(pyvoronoi_scaling)
    for p in grid:
        voro.AddPoint(p.xy)
    voro.Construct()
    pv_cells = voro.GetCells()
    
    cells = []
    for i, pv_cell in enumerate(pv_cells):
        if pv_cell.is_open:
            continue
        polygon = []
        for edge_index in pv_cell.edges:
            e = voro.GetEdge(edge_index)
            start = voro.GetVertex(e.start)
            polygon.append(Point3d(
                start.X,
                start.Y,
                grid[pv_cell.site].z
            ))
        cells.append(Cell(
            Point3d(*grid[pv_cell.site]),
            polygon,
        ))
    return cells


def offset(cells, distance, join_type=JOIN_MITER):
    '''
    Offset all `cells` by a certain unit `distance`.
    Use a negative `distance` to inset cells.
    
    Args:
        cells (list[Cell]): the polygons to offset.
        distance (float): the amount of offset, in units relative to cell size\
            (start with e.g. `0.1`)
        
        join_type (enum): one of `JOIN_SQUARE`, `JOIN_ROUND` or `JOIN_MITER`
        
            .. Note::
    
                Don't generally use `JOIN_ROUND`, it will create *a lot* of
                vertices approximating the rounding which will make the SVGs
                too large to handle.

    '''
    for cell in cells:
        cell.polygon = offset_polygon(cell.polygon, distance, join_type)


def offset_polygon(polygon, distance, join_type=JOIN_MITER):
    '''
    Offsets a the vertices of a `polygon` by `distance` units. Negative
    `distance` insets the polygon.
    
    See :py:func:`offset` for details.
    
    >>> offset_polygon([Point3d(0,0,0), Point3d(2,0,0), Point3d(2,2,0), Point3d(0,2,0), Point3d(0,0,0)], 0.5)
    [Point3d(2.5, 2.5, 0), Point3d(-0.5, 2.5, 0), Point3d(-0.5, -0.5, 0), Point3d(2.5, -0.5, 0), Point3d(2.5, 2.5, 0)]
    
    Note: The point order is not stable!
    
    >>> offset_polygon([Point3d(0,0,0), Point3d(2,0,0), Point3d(2,2,0), Point3d(0,2,0), Point3d(0,0,0)], -0.5)
    [Point3d(1.5, 1.5, 0), Point3d(0.5, 1.5, 0), Point3d(0.5, 0.5, 0), Point3d(1.5, 0.5, 0), Point3d(1.5, 1.5, 0)]
    '''
    poly2d = [p.xy for p in polygon]
    clipper = clip.PyclipperOffset()
    clipper.AddPath(clip.scale_to_clipper(poly2d), join_type, clip.ET_CLOSEDPOLYGON)
    solution = clip.scale_from_clipper(clipper.Execute(clip.scale_to_clipper(distance)))
    try:
        return [Point3d(*p) for p in solution[0]] + [Point3d(*solution[0][0])]
    except IndexError:
        return []


def slant_random(cells, max_slant, max_z_displace=0, seed=None):
    '''
    Randomly slant and z-translate cells of a voronoi graph.
    Slant is z-per-horizontal-distance, so typically 0.1 or lower.
    
    The `slant` parameter is the scaling factor for a random value given to
    each cell.
    `z_displace` is the scale for an additional random offset in z-direction.
    
    >>> cells = voronoi_polygons(grid((3,3)))
    >>> slant_random(cells, 0.1, 0.1)
    '''
    random.seed(seed)
    for cell in cells:
        slant_direction = random.random() * 2 * m.pi
        slant_amount = random.random() * max_slant
        z_displace = random.random() * max_z_displace
        cell.polygon = slant_polygon(
            cell.polygon,
            cell.center,
            slant_direction,
            slant_amount,
            z_displace
        )
        if slant_amount > 0:
            cell.is_slanted = True


def slant_polygon(polygon, center, direction, slant, z_displace):
    '''
    Slant a single polygon relative to its center in the direction given. Note
    that this is a shearing operation, not a rotation. If the z-coordinate
    becomes negative (i.e. *higher* than 0) the whole polygon will be offset
    in positive z-direction to compensate.
    
    Args:
        polygon (list[(float, float, float)]): A float polygon in 3D.
        center ((float, float, float)): Center point around which to shear.
        direction (float): Angle in radians, counter-clockwise from the
            positive x-axis, with the vertices along the direction receiving
            the greatest positive offset, the ones opposite the direction
            receiving the greatest negative offset and vertices at 90° from it
            not changing in z-direction at all.
        slant (float): The shearing amount.
        z_displace (float): An additional z-offset to add to all points in the
            polygon.
    '''
    slanted = []
    min_z = Point3d(0, 0, 1e9)  # larger than any sensible z-location
    for point in polygon:
        distance = point.xy - center.xy
        slant_dir = Point2d(m.cos(direction), m.sin(direction)) * slant
        slant_offset = distance.x * slant_dir.x + distance.y * slant_dir.y
        slanted_point = point + Point3d(z=round(slant_offset))
        if min_z.z > slanted_point.z:
            min_z = slanted_point
        slanted.append(slanted_point)
    slant_compensation = -min_z.z if min_z.z < 0 else 0
    displaced = []
    for point in slanted:
        displaced_point = point + Point3d(z=round(z_displace + slant_compensation))
        displaced.append(displaced_point)
    return displaced


def remove_random_cells(cells, count, grid_size, wrap_amount, scale=1.0, seed=None):
    '''
    Remove `count` random cells (make sure they are visible before!).
    
    Args:
        cells (list[cell]): The graph.
        count (int): Number of cells to remove.
        grid_size ((int, int)): x,y size of the graph.
        wrap_amount (int): Amount of wrapped cells. Needed for visibility
            determination.
        scale (float): The internal scaling factor.
    '''
    inverted_cells = []
    random.seed(seed)
    for i in range(count):
        cell_indices = range(len(cells))
        rindex = random.choice(cell_indices)
        tries = 1000
        while not _cell_visible(cells[rindex], grid_size, wrap_amount, scale) and tries > 0:
            rindex = random.choice(cell_indices)
            tries -= 1
        if tries <= 0:
            rindex = len(cells) // 2
        cell = cells[rindex]
        mirror_cells = [cell] + _get_wrapped_cells(cells, cell, grid_size, scale)
        icells = deepcopy(mirror_cells)
        
        for c in mirror_cells:
            cells.remove(c)
        
        for c in icells:
            c.center.z = 0
            for p in c.polygon:
                p.z = 0
        inverted_cells += icells
    return inverted_cells


def apply_random_texture(cells, texture_images, grid_size, scale=1.0):
    '''
    Set a random texture image with random rotation for each cell.
    
    Args:
        cells (list[cell]): The graph.
        texture_images (list[str]): A list of paths to images.
        grid_size ((int, int)): x,y size of the graph.
        scale (float): The internal scaling factor.
    '''
    if texture_images:
        cells = deepcopy(cells)
        for cell in cells:
            texture = random.choice(texture_images)
            mirror_cells = [cell] + _get_wrapped_cells(cells, cell, grid_size, scale)
            for c in mirror_cells:
                c.texture = {
                    'file': path.abspath(texture),
                    'transform': 'rotate({}, 50%, 50%)'.format(random.randint(0,359))
                }
        return cells
    return None


def _cell_visible(cell, grid_size, wrap_amount, scale=1.0):
    '''.. TODO(jakob):: Document me!'''
    x_visible = (wrap_amount//2 * scale) <= cell.center.x <= ((grid_size[0] + wrap_amount//2) * scale)
    y_visible = (wrap_amount//2 * scale) <= cell.center.y <= ((grid_size[1] + wrap_amount//2) * scale)
    return x_visible and y_visible


def _get_wrapped_cells(cells, cell, grid_size, scale=1.0):
    '''
    Returns:
        Cells which are the wrapped counterpart of the given `cell`.
    
    >>> g = grid((4,4))
    >>> g = wrap(g, (4,4), 4)
    >>> cells = voronoi_polygons(g)
    >>> len(_get_wrapped_cells(cells, cells[6], (4,4)))
    3
    '''
    wrapped_cells = []
    epsilon = 0.1
    cc = cell.center
    for test_cell in cells:
        tc = test_cell.center
        same = abs(tc - cc)
        plus_gridsize = abs(tc - (cc + (Point2d(*grid_size) * scale)))
        minus_gridsize = abs(tc - (cc - (Point2d(*grid_size) * scale)))
        if ((plus_gridsize.x  < epsilon and same.y           < epsilon) or
            (minus_gridsize.x < epsilon and same.y           < epsilon) or
            (plus_gridsize.y  < epsilon and same.x           < epsilon) or
            (minus_gridsize.y < epsilon and same.x           < epsilon) or
            (plus_gridsize.x  < epsilon and plus_gridsize.y  < epsilon) or
            (plus_gridsize.x  < epsilon and minus_gridsize.y < epsilon) or
            (minus_gridsize.x < epsilon and plus_gridsize.y  < epsilon) or
            (minus_gridsize.x < epsilon and minus_gridsize.y < epsilon)):
            wrapped_cells.append(test_cell)
    return wrapped_cells
