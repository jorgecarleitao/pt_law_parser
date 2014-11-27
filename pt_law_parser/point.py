class Point(object):
    """
    A point with two coordinates that can be compared and used in sets.
    """
    def __init__(self, point):
        self._x = point[0]
        self._y = point[1]

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

    def __iter__(self):
        return iter([self._x, self._y])

    def __str__(self):
        return '%d,%d' % (self._x, self._y)

    def __repr__(self):
        return '<%s (%s)>' % (self.__class__.__name__, str(self))
