# CC0 - free software.
# To the extent possible under law, all copyright and related or neighboring
# rights to this work are waived.
'''
2D, 3D and 4D point classes with various basic operators and operations
defined. Operators accept not only Point objects but any list-like object with
values.

>>> p1 = Point2d(x=4, y=1)
>>> p1.x
4
>>> p2 = Point2d(6, -5)
>>> p1 + p2
Point2d(10, -4)
>>> p2 * (2, 0.3)
Point2d(12, -1.5)
>>> p1.distance(p2)
6.324555320336759

`Swizzles`_ can be used to create arbitrary permutations:

>>> p3 = Point3d(1, 4, -3)
>>> p4 = Point4d(7, -9, 8, 7.4)
>>> p3.zy, p4.wzxy, p4.wwyy, p2.yy
(Point2d(-3, 4), Point4d(7.4, 8, 7, -9), Point4d(7.4, 7.4, -9, -9), Point2d(-5, -5))

Calculate the euclidean distance:

>>> p3.veclen()
5.0990195135927845

Various access methods are available:

>>> p3.y
4
>>> p3[1]
4
>>> p3['y']
4

>>> print(*p3)
1 4 -3
>>> 'z' in p3
True
>>> sum(p3)
2
>>> p3 > 0
(True, True, False)
>>> any(p3 <= 0)
True

Very basic color support is also included:

>>> rgb = ColorRgb(255, 10, 100)
>>> rgb.g
10
>>> rgb.gbr
ColorRgb(10, 100, 255)

Allowed colors values are either positive integers or floats between 0 and 1 (inclusive).

>>> invalid_float = ColorRgb(2.3, 0, 0)
Traceback (most recent call last):
    ...
ValueError: color value outside range (0, 1): 2.3
>>> invalid_neg = ColorRgb(-200, 0, 0)
Traceback (most recent call last):
    ...
ValueError: color value cannot be negative: -200

.. _Swizzles:
    https://en.wikipedia.org/wiki/Swizzling_(computer_graphics)
'''
import math
import itertools
from copy import deepcopy


class BasePoint:
    components = []
    coercion = None
    def __init__(self, *args, **kwargs):
        args = list(args)
        for c in self.components:
            if type(self).coercion is not None:
                setattr(self, c, type(self).coercion(kwargs[c] if c in kwargs else (args.pop(0) if len(args) > 0 else 0)))
            else:
                setattr(self, c, kwargs[c] if c in kwargs else (args.pop(0) if len(args) > 0 else 0))
    # indexed access
    def __getitem__(self, index):
        if index in range(len(self.components)):
            return getattr(self, self.components[index])
        elif index in self.components:
            return getattr(self, index)
        else: raise IndexError('Point index out of range')
    # arithmetic operators
    def __add__(self, other):
        try: return type(self)(*[getattr(self, self.components[i]) + other[i] for i in range(len(other))])
        except TypeError: return type(self)(*[getattr(self, c) + other for c in self.components])
    def __sub__(self, other):
        try: return type(self)(*[getattr(self, self.components[i]) - other[i] for i in range(len(other))])
        except TypeError: return type(self)(*[getattr(self, c) - other for c in self.components])
    def __mul__(self, other):
        try: return type(self)(*[getattr(self, self.components[i]) * other[i] for i in range(len(other))])
        except TypeError: return type(self)(*[getattr(self, c) * other for c in self.components])
    def __truediv__(self, other):
        try: return type(self)(*[getattr(self, self.components[i]) / other[i] for i in range(len(other))])
        except TypeError: return type(self)(*[getattr(self, c) / other for c in self.components])
    def __floordiv__(self, other):
        try: return type(self)(*[getattr(self, self.components[i]) // other[i] for i in range(len(other))])
        except TypeError: return type(self)(*[getattr(self, c) // other for c in self.components])
    def __mod__(self, other):
        try: return type(self)(*[getattr(self, self.components[i]) % other[i] for i in range(len(other))])
        except TypeError: return type(self)(*[getattr(self, c) % other for c in self.components])
    def __neg__(self): return type(self)(*[-(getattr(self, c)) for c in self.components])
    def __pos__(self): return self
    # numerical properties
    def __abs__(self): return type(self)(*[abs(getattr(self, c)) for c in self.components])
    def __round__(self): return type(self)(*[round(getattr(self, c)) for c in self.components])
    def __int__(self): return type(self)(*[int(getattr(self, c)) for c in self.components])
    def __float__(self): return type(self)(*[float(getattr(self, c)) for c in self.components])
    # comparisons
    def __gt__(self, other):
        try: return tuple(getattr(self, self.components[i]) > other[i] for i in range(len(other)))
        except TypeError: return tuple(getattr(self, c) > other for c in self.components)
    def __lt__(self, other):
        try: return tuple(getattr(self, self.components[i]) < other[i] for i in range(len(other)))
        except TypeError: return tuple(getattr(self, c) < other for c in self.components)
    def __ge__(self, other):
        try: return tuple(getattr(self, self.components[i]) >= other[i] for i in range(len(other)))
        except TypeError: return tuple(getattr(self, c) >= other for c in self.components)
    def __le__(self, other):
        try: return tuple(getattr(self, self.components[i]) <= other[i] for i in range(len(other)))
        except TypeError: return tuple(getattr(self, c) <= other for c in self.components)
    def __eq__(self, other):
        try: return tuple(getattr(self, self.components[i]) == other[i] for i in range(len(other)))
        except TypeError: return tuple(getattr(self, c) == other for c in self.components)
    # container properties
    def __len__(self): return len(self.components)
    def __contains__(self, component): return component in self.components
    def __iter__(self):
        for c in self.components:
            yield getattr(self, c)
    # object properties
    def __deepcopy__(self, memo): return type(self)(*[getattr(self, c) for c in self.components])
    def __str__(self): return '(' + ', '.join([str(getattr(self, c)) for c in self.components]) + ')'
    def __repr__(self):
        return type(self).__name__ + '(' + ', '.join([
            str(getattr(self, c)) for c in self.components
            # '{}={}'.format(c, getattr(self, c)) for c in self.components
        ]) + ')'
    
    # actual methods
    def distance(self, other):
        '''Calculate the euclidean distance from another point.'''
        return math.sqrt(sum([(other[i] - getattr(self, c))**2 for i, c in enumerate(self.components)]))
    def veclen(self):
        '''Calculate the euclidean distance from the origin.'''
        return self.distance(type(self)())
    
    @classmethod
    def _make_swizzles(cls, partial_classes=[]):
        '''Dynamically generate swizzles: xy, yx, xyz, yxz, xzy, and
           so forth by creating class properties. '''
        swizzle_classes = partial_classes + [cls]
        perm_len_offset = max(0, len(cls.components) - len(partial_classes))
        for i, swizzle_class in enumerate(swizzle_classes):
            for c_order in itertools.product(cls.components, repeat=perm_len_offset + i):
                setattr(cls, ''.join(c_order), property(cls._make_swizzle(swizzle_classes[i], c_order)))
    @classmethod
    def _make_swizzle(cls, return_class, components):
        '''Swizzle factory. Needed because of python's late binding.'''
        def swizzle(self):
            return return_class(*[self[c] for c in deepcopy(components)])
        return swizzle


### Numeric Points

def _number(value):
    '''
    Coerce components to a number, if possible. Does what :py:meth:`int` does
    if it's an integer, otherwise, does what :py:meth:`float` does.
    '''
    f = float(value)
    if f % 1.0 == 0:
        return int(f)
    else:
        return f

class BaseNumericPoint(BasePoint):
    coercion = _number

class Point2d(BaseNumericPoint):
    '''A point in two dimensions.'''
    components = ['x', 'y']
Point2d._make_swizzles()

class Point3d(BaseNumericPoint):
    '''A point in three dimensions.'''
    components = ['x', 'y', 'z']
Point3d._make_swizzles([Point2d])

class Point4d(BaseNumericPoint):
    '''A point in four dimensions. The fourth dimension is `w`.'''
    components = ['x', 'y', 'z', 'w']
# At this point one _make_swizzles()-line creates 300 properties (or 336
# without inheritance from Point3d)
Point4d._make_swizzles([Point2d, Point3d])


class Point2dTex(BaseNumericPoint):
    '''Two-dimensional texture coordinates in `u` and `v`. '''
    components = ['u', 'v']
Point2dTex._make_swizzles()


### Colors

def _color(value):
    '''
    Coerce components to a color value. Either a positive integer, or a float
    between 0.0 and 1.0.
    '''
    f = float(value)
    if f % 1.0 == 0:
        if f >= 0:
            return int(f)
        else:
            raise ValueError('color value cannot be negative: {}'.format(value))
    elif 0 <= f <= 1:
        return f
    else:
        raise ValueError('color value outside range (0, 1): {}'.format(value))


class BaseColor(BasePoint):
    coercion = _color

class ColorRgb(BaseColor):
    '''A color with `r`, `g` and `b` channels.'''
    components = ['r', 'g', 'b']
ColorRgb._make_swizzles()

class ColorHsv(BaseColor):
    '''A color in HSV space.'''
    components = ['h', 's', 'v']

class ColorHsl(BaseColor):
    '''A color in HSL space.'''
    components = ['h', 's', 'l']
    @property
    def hls(self): return ColorHls(self.h, self.l, self.s)

class ColorHls(BaseColor):
    '''A color in HLS space with luminance and saturation exchanged.'''
    components = ['h', 'l', 's']
    @property
    def hsl(self): return ColorHsl(self.h, self.s, self.l)
