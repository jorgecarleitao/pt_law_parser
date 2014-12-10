from math import ceil

from pdfminer.layout import LTTextBox, LTItem


class LTTextColumn(LTTextBox):

    def analyze(self, laparams):
        # sort object up to down, and then by left to right
        self._objs = sorted(self._objs,
                            key=lambda obj: (ceil(obj.y0), ceil(obj.x0)),
                            reverse=True)


class LTTextHeader(LTTextBox):

    def analyze(self, laparams):
        # sort object left to right and then up to down
        self._objs = sorted(self._objs,
                            key=lambda obj: (ceil(obj.x0), ceil(obj.y0)),
                            reverse=True)


class LTNetwork(LTItem):
    def __init__(self):
        super(LTNetwork, self).__init__()
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

    def add(self, point):
        self.points.add(point)

    def add_link(self, point, point_prime):
        assert(point in self and point_prime in self)
        if point not in self.links:
            self.links[point] = set()
        self.links[point].add(point_prime)

        if point_prime not in self.links:
            self.links[point_prime] = set()
        self.links[point_prime].add(point)

    def remove_point(self, point):
        self.points.remove(point)
        del self._links[point]

    def replace(self, old_node, new_node):
        """
        Replaces the node (e.g. move its position).
        """
        self.add(new_node)
        for link in self.links[old_node]:
            self.add_link(new_node, link)

        for point in self._points:
            if old_node in self.links[point]:
                self.links[point].remove(old_node)

        self.remove_point(old_node)

    def print_links(self):
        links = set()
        for point in self.links:
            for link in self.links[point]:
                if (link, point) not in links and (point, link) not in links:
                    links.add((point, link))

        print('{%s}' % ','.join('{%s,%s}' % ('{%s}' % point, '{%s}' % link)
                                for point, link in links))

    def print_nodes(self):
        print('{%s}' % ','.join('{%s}' % point for point in self._points))
