class UndirectedNetwork(object):
    """
    An undirected network has a list of points p_i and links p_i<->p_j.
    There are no self-links (i.e. p_i<->p_i is forbidden).
    """
    def __init__(self):
        self._points = set()
        self._links = dict()

    @property
    def points(self):
        return self._points

    def __iter__(self):
        return iter(self.points)

    def __len__(self):
        return len(self.points)

    @property
    def links(self):
        return self._links

    def add_point(self, point):
        if point not in self._points:
            self._points.add(point)
            self._links[point] = set()

    def remove_point(self, point):
        assert(point in self)

        # remove links from other points
        for point_prime in self._links[point]:
            self._links[point_prime].remove(point)

        # remove links
        del self._links[point]

        # remove point
        self._points.remove(point)

    def add_link(self, point, point_prime):
        assert(point != point_prime)
        assert(point in self and point_prime in self)

        self._links[point].add(point_prime)
        self._links[point_prime].add(point)

        self.assert_consistency()

    def remove_link(self, point, point_prime):
        assert(point in self and point_prime in self)
        assert(point_prime in self.links[point] and
               point in self._links[point_prime])

        self._links[point].remove(point_prime)
        self._links[point_prime].remove(point)

    def links_list(self):
        links = []
        for point in self.links:
            for link in self.links[point]:
                if (link, point) not in links and (point, link) not in links:
                    points = sorted((point, link), key=lambda p: (p.x, p.y))
                    links.append(tuple(points))
        return links

    def print_links(self):
        print('{%s}' % ','.join('{%s,%s}' % ('{%s}' % point, '{%s}' % link)
                                for point, link in self.links_list()))

    def print_nodes(self):
        print('{%s}' % ','.join('{%s}' % point for point in self._points))

    def assert_consistency(self):
        for point in self:
            for link in self.links[point]:
                if point not in self.links[link]:
                    assert(False)
