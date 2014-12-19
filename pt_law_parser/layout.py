from collections import defaultdict
from math import ceil

from pdfminer.layout import LTExpandableContainer, LTItem

from pt_law_parser.point import Point


class LTTextColumn(LTExpandableContainer):

    def analyze(self, laparams):
        # sort object up to down, and then by left to right
        self._objs = sorted(self._objs,
                            key=lambda obj: (ceil(obj.y0), ceil(obj.x0)),
                            reverse=True)

    def expand_left(self, x0):
        self._bbox = (min(self.x0, x0), self.y0, self.x1, self.y1)

    def expand_right(self, x1):
        self._bbox = (self.x0, self.y0, max(self.x1, x1), self.y1)


class LTTextHeader(LTExpandableContainer):

    def analyze(self, laparams):
        # sort object left to right and then up to down
        self._objs = sorted(self._objs,
                            key=lambda obj: (ceil(obj.x0), ceil(obj.y0)),
                            reverse=True)


class LTPageLayout(object):

    MIDDLE_X1 = (292 + 306.0)/2

    def __init__(self):
        self.header = LTTextHeader()
        self.center = []
        self.left = []
        self.right = []

        self._previous_column = None

    def get_center_column(self, item):
        columns = sorted(self.center, key=lambda c: c.y0, reverse=True)

        def new_column():
            c = LTTextColumn()
            self.center.append(c)
            return c

        if not columns:
            return new_column()

        if item.y0 > columns[0].y0:
            if self.left and item.y0 > self.left[-1].y0 > columns[0].y0:
                # is above first but there is column in the middle
                return new_column()
            else:
                return columns[0]
        elif item.y0 < columns[-1].y0:
            if self.left and item.y0 < self.left[-1].y0 < columns[-1].y0:
                # is below last but there is column in the middle
                return new_column()
            else:
                return columns[-1]

        # is in the middle of two columns, get the first one.
        for column in columns:
            if item.y0 < column:
                return column

        assert(False)

    def add(self, item):
        if item.x0 < item.x1 < self.MIDDLE_X1:
            if not self.left:
                self.left.append(LTTextColumn())
            column = self.left[-1]
        elif self.MIDDLE_X1 < item.x0 < item.x1:
            if not self.right:
                self.right.append(LTTextColumn())
            column = self.right[-1]
        else:
            column = self.get_center_column(item)
        column.add(item)

    def add_line(self, line, is_title):
        if line.x0 < line.x1 < self.MIDDLE_X1:
            if not self.left:
                self.left.append(LTTextColumn())
            column = self.left[-1]

            if self._previous_column and self._previous_column in self.center and \
                    len(self.center[-1]):
                if not is_title(line, column):
                    column = self.center[-1]

        elif self.MIDDLE_X1 < line.x0 < line.x1:
            if not self.right:
                self.right.append(LTTextColumn())
            column = self.right[-1]
        else:
            column = self.get_center_column(line)

        column.add(line)
        self._previous_column = column

    def add_header(self, line):
        self.header.add(line)

    def analyze(self):
        for element in [self.header] + self.center + self.left + self.right:
            element.analyze(None)

    def is_empty(self):
        return not (self.center or self.left)

    def expand_left(self, x0, x1):
        for left_column in self.left:
            left_column.expand_left(x0)
            left_column.expand_right(x1)

    def expand_right(self, x0, x1):
        for right_column in self.right:
            right_column.expand_left(x0)
            right_column.expand_right(x1)

    def assert_non_overlapping(self):
        """
        Asserts that the layouts are not overlapping.
        """
        for layout in self.center:
            for layout_prime in self.left:
                if len(layout) and len(layout_prime):
                    assert(not (layout_prime.voverlap(layout) and
                                layout_prime.hoverlap(layout)))

    def ordered_columns(self):
        """
        Returns the list of columns ordered according to the reading order.
        """
        if self.is_empty():
            return []

        self.assert_non_overlapping()

        left = sorted(self.left, key=lambda c: c.y0, reverse=True)
        right = sorted(self.right, key=lambda c: c.y0, reverse=True)

        class LTAlignedColumns:
            """
            An auxiliar class to sort centered columns and aligned columns.
            """
            def __init__(self, left, right):
                self.left = left
                self.right = right

            @property
            def y0(self):
                return self.left.y0

        aligned_columns = []
        right_columns_paired = []
        for l_column in left:
            was_found = False
            for r_column in right:
                if l_column.voverlap(r_column):
                    aligned_columns.append(LTAlignedColumns(l_column, r_column))
                    was_found = True
                    right_columns_paired.append(r_column)
                    break
            if not was_found:
                aligned_columns.append(l_column)

        # right columns must always be paired
        assert(len(right_columns_paired) == len(right))

        # sort centered and aligned columns.
        columns = sorted(self.center + aligned_columns,
                         key=lambda c: c.y0, reverse=True)

        # recover the aligned columns
        result = []
        for c in columns:
            if isinstance(c, LTAlignedColumns):
                result.append(c.left)
                result.append(c.right)
            else:
                result.append(c)
        return result


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
        assert(point != point_prime)
        assert(point in self and point_prime in self)
        if point not in self.links:
            self.links[point] = set()
        self.links[point].add(point_prime)

        if point_prime not in self.links:
            self.links[point_prime] = set()
        self.links[point_prime].add(point)

    def remove_link(self, point, point_prime):
        assert(point in self and point_prime in self)
        assert(point_prime in self.links[point] and
               point in self.links[point_prime])

        self.links[point].remove(point_prime)
        self.links[point_prime].remove(point)

    def remove_point(self, point):
        self.points.remove(point)
        del self._links[point]

    def replace(self, old_node, new_node):
        """
        Replaces the node (e.g. move its position).
        """
        self.add(new_node)

        if self.links[old_node] == {new_node}:
            # two points that merge together without other link interfering.
            self.links[new_node] = set()
            self.remove_point(old_node)
            return

        for link in self.links[old_node]:
            self.add_link(new_node, link)

        for point in self._points:
            if old_node in self.links[point]:
                self.links[point].remove(old_node)

        self.remove_point(old_node)

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

    def _remove_duplicates(self):
        """
        Removes duplicated points close to each other.
        """
        # select points to remove by proximity
        points_to_remove = set()
        for point in self:
            for point_prime in self:
                if point != point_prime and\
                        abs(point_prime.x - point.x) <= 2 and\
                        abs(point_prime.y - point.y) <= 2 and\
                        (point_prime, point) not in points_to_remove:
                    points_to_remove.add((point, point_prime))

        removed_points = set()
        for point, point_prime in points_to_remove:
            if point in removed_points:
                continue

            for link_prime in self.links[point_prime]:
                self.links[point].add(link_prime)
                self.links[link_prime].add(point)
                self.links[link_prime].remove(point_prime)

            # track removed points
            removed_points.add(point_prime)
            self.remove_point(point_prime)

    def _align_nodes(self):
        """
        Makes the links horizontal/vertical by aligning nodes.
        """
        # make an histogram of the most common x and y values
        raw_x_values = defaultdict(int)
        raw_y_values = defaultdict(int)
        for point in self:
            raw_x_values[point.x] += 1
            raw_y_values[point.y] += 1

        # stores which values to replace (remove close values)
        replace_x = {}
        for x in raw_x_values:
            for x_prime in raw_x_values:
                if x != x_prime and abs(x - x_prime) < 5:
                    if raw_x_values[x_prime] > raw_x_values[x]:
                        replace_x[x] = x_prime
                    elif raw_x_values[x_prime] == raw_x_values[x]:
                        # in case they are the same, we must ensure
                        # we don't substitute both by each other.
                        if x > x_prime:
                            replace_x[x] = x_prime
                        else:
                            replace_x[x_prime] = x
                    else:
                        replace_x[x_prime] = x

        replace_y = {}
        for y in raw_y_values:
            for y_prime in raw_y_values:
                if y != y_prime and abs(y - y_prime) < 5:
                    if raw_y_values[y_prime] > raw_y_values[y]:
                        replace_y[y] = y_prime
                    elif raw_y_values[y_prime] == raw_y_values[y]:
                        # in case they are the same, we must ensure
                        # we don't substitute both by each other.
                        if y > y_prime:
                            replace_y[y] = y_prime
                        else:
                            replace_y[y_prime] = y
                    else:
                        replace_y[y_prime] = y

        for point in list(self)[:]:
            if point.x in replace_x:
                self.replace(point, Point((replace_x[point.x], point.y)))

        for point in list(self)[:]:
            if point.y in replace_y:
                self.replace(point, Point((point.x, replace_y[point.y])))

    def _remove_siblings(self):
        """
        Removes nodes with only two links (are not important for table creation).
        """
        points_to_remove = set()
        for point in self:
            if len(self.links[point]) == 2:
                point1 = list(self.links[point])[0]
                point2 = list(self.links[point])[1]
                assert(point1.x == point.x == point2.x or
                       point1.y == point.y == point2.y)

                self.links[point1].remove(point)
                self.links[point1].add(point2)

                self.links[point2].add(point1)
                self.links[point2].remove(point)

                points_to_remove.add(point)

        for point in points_to_remove:
            self.remove_point(point)

    def _get_components(self):
        """
        Returns a list of non-overlapping networks.
        """
        networks = []

        def add_point(network, point):
            """
            Recursively adds a point and respective connected component to
            network.
            """
            network.add(point)
            for link in self.links[point]:
                if link not in network:
                    add_point(network, link)
                network.add_link(point, link)

        for point in self.points:
            # try to find the network of this point.
            found = None
            for network in networks:
                if point in network:
                    found = network
                    break

            # if no network exists, create one for it.
            if found is None:
                networks.append(LTNetwork())
                found = networks[-1]

            # finally, add its connected component to the network.
            add_point(found, point)

            # asserts that the connected component is on that network only.
            for link in self.links[point]:
                assert(link in found)
                for network in networks:
                    if network != found:
                        assert(point not in network)
                        assert(link not in network)

        # asserts that we didn't lost any point
        assert(sum(len(network) for network in networks) ==
               len(self))

        return networks

    def create_components(self):
        self._remove_duplicates()
        self._align_nodes()

        self._fix_intersections()
        self._fix_missing_links()

        self._remove_siblings()

        self.assert_strait_links()
        self.assert_no_intersections()

        return self._get_components()

    def assert_strait_links(self):
        links = self.links_list()
        for link in links:
            assert(link[0].x == link[1].x or link[0].y == link[1].y)

    def assert_no_intersections(self):
        links = self.links_list()
        for link in links:
            for link_prime in links:
                if intersect(link[0], link[1], link_prime[0], link_prime[1]):
                    raise Exception(link, link_prime)

    def _fix_intersections(self):
        """
        Computes all intersections of links and creates points in the
        intersections, subdividing the links accordingly.
        """
        links = self.links_list()

        vertical_links = [link for link in links if link[0].x == link[1].x]
        horizontal_links = [link for link in links if link[0].y == link[1].y]
        assert(len(links) == len(vertical_links) + len(horizontal_links))

        v_links_to_subdivide = defaultdict(set)
        h_links_to_subdivide = defaultdict(set)
        for link in vertical_links:
            for link_prime in horizontal_links:
                if intersect(link[0], link[1], link_prime[0], link_prime[1]):
                    point = Point((link[0].x, link_prime[0].y))
                    v_links_to_subdivide[link].add(point)
                    h_links_to_subdivide[link_prime].add(point)

        for link in h_links_to_subdivide:
            points = sorted(h_links_to_subdivide[link], key=lambda p: p.x)
            self._subdivide(link[0], link[1], points)
        for link in v_links_to_subdivide:
            points = sorted(v_links_to_subdivide[link], key=lambda p: p.y)
            self._subdivide(link[0], link[1], points)

    def _fix_missing_links(self):
        """
        Computes all points that are crossed by a line without a link and
        subdivides such line to link it with those points.
        """
        previous_number_of_points = len(self)

        links = self.links_list()

        vertical_links = [link for link in links if link[0].x == link[1].x]
        horizontal_links = [link for link in links if link[0].y == link[1].y]

        found_points = dict()
        for link in horizontal_links:
            points = [p for p in self if p.y == link[0].y and
                      link[0].x < p.x < link[1].x]
            if points:
                found_points[link] = points

        for link in found_points:
            points = sorted(found_points[link], key=lambda p: p.x)
            self._subdivide(link[0], link[1], points)

        found_points = dict()
        for link in vertical_links:
            points = [p for p in self if p.x == link[0].x and
                                  link[0].y < p.y < link[1].y]
            if points:
                found_points[link] = points

        for link in found_points:
            points = sorted(found_points[link], key=lambda p: p.y)
            self._subdivide(link[0], link[1], points)

        # asserts that we didn't added any new point
        assert(previous_number_of_points == len(self))

    def _subdivide(self, first_point, last_point, points):
        """
        Subdivides the link first_point<->last_point into links

            first_point<->points[0]<->...<->points[-1]<->last_point.

        Assumes `points` are sorted.
        """
        assert(len(points) > 0)
        self.remove_link(first_point, last_point)

        for point in points:
            self.add(point)

        if len(points) == 1:
            self.add_link(first_point, points[0])
            self.add_link(points[0], last_point)
            return

        for i, point in enumerate(points):
            if i == 0:
                point_before = first_point
                point_after = points[i + 1]
            elif i == len(points) - 1:
                point_before = points[i - 1]
                point_after = last_point
            else:
                point_before = points[i - 1]
                point_after = points[i + 1]
            self.add_link(point_before, point)
            self.add_link(point, point_after)


def ccw(a, b, c):
    return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x)


# Return true if line segments ab and cd intersect
def intersect(a, b, c, d):
    # if the intersection is *exactly* on a point, we ignore it.
    count_x = defaultdict(int)
    count_y = defaultdict(int)
    for p in (a, b, c, d):
        count_x[p.x] += 1
        count_y[p.y] += 1
    for x in count_x:
        if count_x[x] == 3:
            return False
    for y in count_y:
        if count_y[y] == 3:
            return False

    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)
