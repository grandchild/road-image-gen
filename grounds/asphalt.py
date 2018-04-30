
import PIL 
from PIL import Image, ImageDraw
import random
import math
from colorsys import rgb_to_hls, hls_to_rgb
from util.point import Point2d


# Colors
def _int_ramp(min_, max_, num):
    '''
    Returns: A list of `num` integers from `min_` to `max_` (inclusive).
    '''
    return [round(v * ((max_-min_) / (num-1))) + min_ for v in range(num)]

COLOR_LIST = [(v,v,v) for v in _int_ramp(0, 98, 40)] + [(v,v,v) for v in _int_ramp(105, 190, 4)]
BLACK = (0,)*3
WHITE = (255,)*3
# Directions and their vectors
NW, N, NE, E, SE, S, SW, W = range(8)
DIR_V = [(-1, -1), (0, -1), (1, -1), (1,  0), (1,  1), (0,  1), (-1,  1), (-1,  0)]



def generate_asphalt(resolution, asphalt_type, img_destination, img_defects_destination, img_depth_destination, crack_length, number_of_cracks, crack_width):
    '''
    Generate 3 kinds of images: texture image, defects image and depth image,
    and save them to files.

    Args:
        resolution ([int, int]): Resolution contains the image width and
            height
        asphalt_type (int): Type of the asphalt
            
            .. TODO:: Testen
        
        img_destination (str): Asphalt texture path
        img_defects_destination (str): Path of the image containing the
            defects
        img_depth_destination (str): Path of the image containing the depth
            information.
        crack_length (float): Size of the crack relative to image width
        number_of_cracks (int): Maximal number of the cracks in a image
        crack_width (int) : Crack width
    '''
    width, height = resolution
    texture_img = Image.new('RGB', resolution, 'white')
    depth_img = Image.new('RGB', resolution, 'white')
    defects_img = Image.new('RGB', resolution, 'black')
    draw = ImageDraw.Draw(texture_img)
    for x in range (texture_img.size[0]):
        for y in range(texture_img.size[1]):
            if asphalt_type == 1:
                rgb_color= random.choice(COLOR_LIST[30:len(COLOR_LIST)])
                draw.point((x,y),rgb_color)
            elif asphalt_type == 2:
                rgb_color = random.choice(COLOR_LIST[3:45])
                draw.point((x,y),rgb_color)
            else:
                rgb_color = random.choice([BLACK, WHITE])
                draw.point((x,y),rgb_color)
    #draw asphalt shapes
    shape_number = 6000
    for z in range(shape_number):
        #generate random center point coordinates for the shapes
        min_max = 1, 3
        p = Point2d(
            random.randint(min_max[1], texture_img.size[0]-min_max[1]),
            random.randint(min_max[1], texture_img.size[1]-min_max[1]),
        )
        inlay_darkening = random.randint(0, 80)
        shape_colors = [(
            v + random.randint(-10, 10),
            v + random.randint(-15, 10),
            v + random.randint(-20, 10),
        ) for v in _int_ramp(169 - inlay_darkening, 220 - inlay_darkening, 4)]
        draw_asphalt_shape(p, texture_img, defects_img, depth_img, shape_colors, min_max)
    ################### generates potholes################################
    #min_max = 9,21
    #for n in range(number_of_cracks):
        #px = random.randint(0,width)
        #py = random.randint(0,height)
        #p = Point2d(px, py)
        #pothole_generater(p, texture_img, defects_img, depth_img, min_max, 30)
    #######################################################################
    generate_cracks(texture_img, defects_img, depth_img, crack_length, crack_width, number_of_cracks)    
    texture_img.save(img_destination)
    defects_img.save(img_defects_destination)
    depth_img.save(img_depth_destination)


def generate_cracks(texture_img, defects_img, depth_img, crack_length, crack_width, number_of_cracks):
    '''
    Generate a given number of cracks.

    Args:
        texture_img (PIL.Image.Image): The texture of the street
        defects_img (PIL.Image.Image): A black-or-white image marking the
            extent and shape of defects
        depth_img (PIL.Image.Image): Depth_Img contains the depth of the
            defects as RGB format
        crack_length (float): Size of the crack relative to image width
        crack_width (int) : Crack width
        number_of_cracks (int): Maximal number of the cracks in a Image

    '''
    img_width = texture_img.size[0]
    img_height = texture_img.size[1]
    max_steps = round(5 * crack_length * img_width / crack_width)
    for j in range(number_of_cracks):
        direction = random.randint(0, 7)
        # Set starting point of the crack in the opposite direction
        p = Point2d(
            random.randint(0, img_width//2)  - DIR_V[direction][0] * (img_width//2),
            random.randint(0, img_height//2) - DIR_V[direction][1] * (img_height//2),
        )
        crack_points = draw_crack(p, direction, max_steps, crack_width, texture_img, defects_img, depth_img)
        for k in range(random.randint(1,5)):
            position = random.choice(crack_points)
            side_direction = (direction + random.choice([-3, -2, -1, 1, 2, 3]) + 8) % 8
            draw_crack(position, side_direction, round(max_steps * (random.random() * 0.5 + 0.1)), 3, texture_img, defects_img, depth_img)


def draw_crack(p, direction, max_steps, crack_width, texture_img, defects_img, depth_img):
    '''
    Draw a crack in the given images. The width of the crack is relative to
    the picture width.

    Args:
        p (Point2d): Starting point
        direction (int): The crack direction in one of eight cardinal
            directions
        max_steps (int): Crack length in steps
        crack_width (int) : Crack width relative to the image width.
        texture_img (PIL.Image.Image): The texture for our ground(Street).
        defects_img (PIL.Image.Image): Defect_img contains the exact defects
        depth_img (PIL.Image.Image): Depth_Img contains the depth of the
            defects as RGB format
    Returns:
        (List of Points): Each Point contains the x,y coordinates of the cracks
    '''
    start_direction = direction
    step_size = round(crack_width * 0.2)
    crack_points = []
    for i in range(max_steps):
        if not (0 <= direction <= 8):
            raise ValueError("Unknown direction: {}".format(direction))
        p += Point2d(*DIR_V[direction]) * step_size
        if not (0 <= p.x <= texture_img.size[0]):
            p.x = p.x - texture_img.size[0]*(-1 if p.x < 0 else 1)
        if not (0 <= p.y <= texture_img.size[1]):
            p.y = p.y - texture_img.size[1]*(-1 if p.y < 0 else 1)
        dynamic_width_crack(p, crack_width, max_steps, i, texture_img, defects_img, depth_img)
        crack_points.append(p)
        new_dir = random.randint(-1,1)
        direction = (start_direction + new_dir + 8) % 8
    return crack_points


def dynamic_width_crack(p, max_width, max_steps, i, texture_img, defects_img, depth_img):
    '''
    Draw cracks onto the asphalt. The cracks are `max_steps` long, and
    `max_width` wide in the middle.

    Args:
        p (Point2d): x,y coordinates of a point
        max_width (int): Maximal width of the cracks
        max_steps (int): Maximal Crack length in pixel
        i (int): Stepsnumber beetwen 0 and max_steps
        texture_img (PIL.Image.Image): The texture for our ground(Street)
        defects_img (PIL.Image.Image): Defect_img contains the exact defects
        depth_img (PIL.Image.Image): Depth_Img contains the depth of the
            defects as RGB format
    '''
    mid_start = max_steps/3
    mid_end = 2*(max_steps/3)
    color = (depth_brightness(max_steps, i),)*3
    min_width = max_width * 0.2
    if 0 <= i <= mid_start:
        draw_asphalt_shape(p, texture_img, defects_img, depth_img, [color], [min_width]*2, defects=True)
        pass
    elif mid_start < i <= mid_end :
        width = math.fabs(math.sin(((i/max_steps)*3-1)*math.pi)*(max_width - min_width) + min_width)
        draw_asphalt_shape(p, texture_img, defects_img, depth_img, [color], [width, width*0.5], defects=True)
    elif mid_end < i <= max_steps:
        draw_asphalt_shape(p, texture_img, defects_img, depth_img, [color], [min_width]*2, defects=True)
        pass
    else:
        raise ValueError("Invalid length index: {}".format(i))




def draw_asphalt_shape(p, texture_img, defects_img, depth_img, colors, min_max, defects=False):
    '''
    Draws a quad into the given images.
    
    Args:
        p (Point2d): x,y coordinates of a point
        texture_img (PIL.Image.Image): The texture for our ground(Street)s
        defects_img (PIL.Image.Image): Defect_img contains the exact defects
        depth_img (PIL.Image.Image): Depth_Img contains the depth of the
            defects as RGB format
        colors (list[(int, int int)]): A list of greyscale colors
        min_max ([int, int]): Min, Max width  of the quad
        defects (bool): If false then it draws defects for the defects_img and
            depth_img otherwise quads for the texture_img
    '''
    draw_texture = ImageDraw.Draw(texture_img, 'RGBA')
    points = random_quad(p, min_max)
    
    if defects:
        draw_defects = ImageDraw.Draw(defects_img)
        draw_defects.polygon(points, WHITE)
        draw_depth = ImageDraw.Draw(depth_img)
        draw_depth.polygon(points, colors[0])
        
        rgb = colors[0][0] / 255.0, colors[0][1] / 255.0, colors[0][2] / 255.0
        hls = rgb_to_hls(*rgb)
        hls = (random.uniform(0.02, 0.1), hls[1]*.1+.1, 0.3)
        rgb = hls_to_rgb(*hls)
        draw_texture.polygon(points, (round(rgb[0]*255), round(rgb[1]*255), round(rgb[2]*255), 40))
    else:
        color = random.choice(colors)
        draw_texture.polygon(points, color)

def draw_quad(p, texture_img, defects_img, depth_img, min_max):
    """
    Draws a quad into the given images.

    Args:
        p (Point2d): x,y coordinates of a point
        texture_img (PIL.Image.Image): The texture for our ground(Street)s
        defects_img (PIL.Image.Image): Defect_img contains the exact defects
        depth_img (PIL.Image.Image): Depth_Img contains the depth of the
            defects as RGB format
        min_max ([int, int]): Min, Max width  of the quad
    """
    points = random_quad(p, min_max)

    draw_defects = ImageDraw.Draw(defects_img)
    draw_defects.polygon(points, WHITE)

    draw_depth = ImageDraw.Draw(depth_img)
    draw_depth.polygon(points, BLACK)

    draw_texture = ImageDraw.Draw(texture_img, 'RGBA')
    draw_texture.polygon(points,BLACK)

def pothole_generater(p, texture_img, defects_img, depth_img, min_max, radius): 
    """
    Draws a pothole into the given images

    Args:
     p (Point2d): x,y coordinates of a point
        texture_img (PIL.Image.Image): The texture for our ground(Street)s
        defects_img (PIL.Image.Image): Defect_img contains the exact defects
        depth_img (PIL.Image.Image): Depth_Img contains the depth of the
            defects as RGB format
        min_max ([int, int]): Min, Max width  of the quad
        radius (int): Max radius of the pothole starting at the given point p
    """
    tempP = p
    for d in range(len(DIR_V)):
        p = tempP
        n = round(random.uniform(3, radius))
        for r in range(n):
            draw_quad(p, texture_img, defects_img, depth_img, min_max)
            p = p+Point2d(*DIR_V[d])


def depth_brightness(max_steps, i):
    '''
    Return the depth as a brightness level along the a crack of length
    `max_steps` at the index `i`.

    Args:
        max_steps (int): Maximal Crack length in pixel
        i (int): Stepsnumber beetwen 0 and max_steps

    Returns:
        (int): Color value for the RGB channels
    '''
    max_depth = 250
    return 255 - round((-math.cos(2*math.pi * i/max_steps) * 0.5 + 0.5) * max_depth)


def random_quad(p, min_max):
    '''
    Create vertices of a quad, with some random variation in *x* and *y* in
    the range `min_max`.
    
    Args:
        p (Point2d): x,y coordinates of a point
        min_max ([int, int]: Min, Max width  of the quad
    
    Returns:
        ([Point2d, Point2d, Point2d, Point2d]): Vertices of the quad
    '''
    v1 = round(point_randrange(p, min_max, DIR_V[NW]))
    v2 = round(point_randrange(p, min_max, DIR_V[SW]))
    v3 = round(point_randrange(p, min_max, DIR_V[SE]))
    v4 = round(point_randrange(p, min_max, DIR_V[NE]))
    return ((v1.x, v1.y), (v2.x, v2.y), (v3.x, v3.y), (v4.x, v4.y))

def point_randrange(p, min_max, direction=(1,1)):
        '''
        Return a point with a random offset within range of `min_max` in
        `direction`.
        
        Args:
            min_max ((float, float) | ((float, float), (float, float))):
                Minimum and maximum for both directions at once, or for each
                direction separately.
        '''
        try:
            r_offset = Point2d(
                random.uniform(min_max[0][0], min_max[1][0]),
                random.uniform(min_max[0][1], min_max[1][1]),
            )
        except TypeError:
            r_offset = Point2d(
                random.uniform(min_max[0], min_max[1]),
                random.uniform(min_max[0], min_max[1]),
            )
        return p + r_offset * direction


if __name__ == '__main__':
    #generate asphalt type 1
    print(len(DIR_V))
    crack_length = 0.75
    number_of_cracks = 3
    crack_width = 10
    resolution = [960,640]
    number_of_pics = 5
    for i in range(number_of_pics):
        asphalt_type = 1
        img_destination = 'output/asphalt_output/random_Asphalt-{}-{}.png'.format(asphalt_type,i)
        img_defects_destination = 'output/asphalt_output/random_asphalt_error-{}-{}.png'.format(asphalt_type,i)
        img_depth_destination = 'output/asphalt_output/random_asphalt_depth-{}-{}.png'.format(asphalt_type,i)
        generate_asphalt(
            resolution,
            asphalt_type,
            img_destination,
            img_defects_destination,
            img_depth_destination,
            crack_length,
            number_of_cracks,
            crack_width,
        )
    #generate asphalt type 2
    #for j in range(5):
        #asphalt_type = 2
        #img_destination = 'output/asphalt_output/random_Asphalt-{}-{}.png'.format(asphalt_type,j)
        #img_defects_destination = 'output/asphalt_output/random_asphalt_error-{}-{}.png'.format(asphalt_type,i)
        #generate_asphalt(resolution,asphalt_type,img_destination,img_defects_destination)
    #for k in range(10):
        #generate_asphalt(3,k)
   
    
