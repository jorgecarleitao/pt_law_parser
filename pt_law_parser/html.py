import re
from collections import defaultdict

from pdfminer.layout import LTComponent, LTImage

from pt_law_parser.auxiliar import eq, middle_x
from pt_law_parser.point import Point


class Paragraph(object):

    @staticmethod
    def sanitize(text):
        # hyphens in words are getting a space from PDFminer. Remove it.
        return re.sub(ur' (\-\w+?)', ur'\1', text, flags=re.U)

    def __init__(self, text):
        assert(text[-1] != '\n')
        self._text = self.sanitize(text.strip())

    def merge(self, other_line):
        text = other_line.text
        if self.text[-1] == '-':
            self._text = self._text[:-1]
        # don't merge two lines without a space in between if no hyphen
        elif text[0] != ' ' and self._text[-1] != ' ':
            text = ' ' + text
        self._text += self.sanitize(text)

    @property
    def text(self):
        return self._text

    def as_html(self):
        return '<p>%s</p>' % self.text


class Header(Paragraph):

    def as_html(self):
        return '<h1>%s</h1>' % self.text


class Table(LTComponent):
    """
    A table performs 3 operations:

    1. receives a network and converts it to a set of cells (__init__)
    2. receives items and maps then to the correct cells (add)
    3. is able to represent itself in HTML (as_html)
    """

    class Element():
        """
        Represents an element of an HTML table. It has a colspan and rowspan.
        """
        def __init__(self, cell):
            self.cell = cell
            self.row = None
            self.column = None
            self.colspan = 0
            self.rowspan = 0

            self._lines = []
            self._min_x = 0
            self._min_y = 0

        @property
        def lines(self):
            return self._lines

        def add(self, row, column):
            if self.row is None:
                self.row = row
                self.column = column
            else:
                if self.row == row:
                    self.colspan += 1
                if self.column == column:
                    self.rowspan += 1

        def add_line(self, item, bbox):
            """
            Adds a line to the cell assuming a bounding box bbox.
            """
            # todo: this code is similar to _parse_line. Common implementation?
            def remove_dots(text):
                return text.replace(' .', '')

            text = remove_dots(item.get_text())
            if text == '.':
                return
            line = Paragraph(text)

            if not self._lines:
                # cell is empty
                self._lines.append(line)
                self._min_x = item.x0
            else:
                middle_x_cell = middle_x(bbox)
                middle_x_line = middle_x(item.bbox)
                is_centered = eq(middle_x_cell, middle_x_line, 1)

                if is_centered:
                    if self._min_y - item.y1 < 0:
                        self._lines[-1].merge(line)
                    else:
                        self._lines.append(line)
                elif eq(self._min_x, item.x0, 1):
                    self._lines.append(line)
                else:
                    self._lines[-1].merge(line)
            self._min_y = item.y0

    class EmptyTableError(Exception):
        """
        Raised by constructor when construction fails because table has no
        cells. This means that the constructed network does not constitute a
        table and should be ignored.
        """
        pass

    def __init__(self, network):
        if len(network) <= 2:
            raise self.EmptyTableError

        # construct rows and columns borders by distinct x and y's.
        self._rows_borders = sorted(list(
            set(point.y for point in network.points)))
        self._columns_borders = sorted(list(
            set(point.x for point in network.points)))

        LTComponent.__init__(self, (self._columns_borders[0],
                                    self._rows_borders[0],
                                    self._columns_borders[-1],
                                    self._rows_borders[-1]))

        self._close_network(network)
        self._create_links(network)
        self._cells = self._create_cells(network)
        self._elements = self._build_elements(self._cells)

    def _close_network(self, network):
        """
        Adds missing corners and border links to close the network.
        """
        # add possible missing corners
        for corner in ((self.x0, self.y0), (self.x0, self.y1), (self.x1, self.y1),
                       (self.x1, self.y0)):
            network.add_point(Point(corner))
        # add possible missing bottom and top borders
        for row in (self._rows_borders[0], self._rows_borders[-1]):
            points = sorted([point for point in network if point.y == row],
                            key=lambda p: p.x)
            for i, point in enumerate(points):
                if i == 0:
                    continue
                network.add_link(points[i - 1], point)

        # add possible missing left and right borders
        for column in (self._columns_borders[0], self._columns_borders[-1]):
            points = sorted([point for point in network if point.x == column],
                            key=lambda p: p.y)
            for i, point in enumerate(points):
                if i == 0:
                    continue
                network.add_link(points[i - 1], point)

    def _create_links(self, network):
        """
        Creates all links between points that are co-linear. These points become
        fully connected.
        """
        links_to_create = set()

        links = network.links  # an alias

        for row in self._rows_borders:
            # all points in this row and sorted by x
            points = sorted([point for point in network if point.y == row],
                            key=lambda p: p.x)

            # a O(N^2) loop that breaks the inner
            # if there is a link-break along the way.
            for index, point in enumerate(points[:-1]):
                index_prime = index + 1  # starting on the following point

                # while there is a link between point at index_prime and
                # the previous point at `index_prime - 1`.
                while index_prime != len(points) and \
                        points[index_prime] in links[points[index_prime - 1]]:
                    # add the link from point to point prime and advance
                    # point prime by one.
                    links_to_create.add((point, points[index_prime]))

                    index_prime += 1

        # Exactly the same loop, but with x<>y and row<>column.
        for column in self._columns_borders:
            points = sorted([point for point in network
                             if point.x == column], key=lambda p: p.y)
            for index, point in enumerate(points[:-1]):
                index_prime = index + 1
                while index_prime != len(points) and \
                        points[index_prime] in links[points[index_prime - 1]]:
                    links_to_create.add((point, points[index_prime]))

                    index_prime += 1

        # finally, add the links
        for point, point_prime in links_to_create:
            network.add_link(point, point_prime)

    @staticmethod
    def _create_cells(network):
        """
        Creates cells from the network and returns then
        as LTComponents.
        """
        squares_taken = defaultdict(set)
        cells = set()

        def city_distance(point, point_prime):
            return abs(point.x - point_prime.x) + abs(point.y - point_prime.y)

        def is_perpendicular(v1_x, v1_y, v2_x, v2_y):
            return v1_x*v2_x + v1_y*v2_y == 0

        for point in sorted(network, key=lambda p: (p.x, p.y)):
            for l1 in sorted(network.links[point],
                             key=lambda p: city_distance(p, point)):
                valid_links = [
                    link for link in network.links[point] if link != l1 and
                    is_perpendicular(link.x - point.x, link.y - point.y,
                                     l1.x - point.x, l1.y - point.y)]

                for l2 in sorted(valid_links,
                                 key=lambda p: city_distance(p, point)):
                    inter = network.links[l2].intersection(network.links[l1])
                    intersection = list(inter)

                    # remove initial point
                    intersection.remove(point)

                    if len(intersection) == 0:
                        continue

                    # sort by areas: smallest area first
                    area = lambda p: (p.x - point.x)*(p.y - point.y)
                    intersection.sort(key=area)

                    # square is formed by [point, l1, l2, last_point], in this
                    # order.
                    points = [point, l1, l2, intersection[0]]

                    # compute middle position of the square
                    middle_x = sum(point.x for point in points)/4.
                    middle_y = sum(point.y for point in points)/4.

                    # check if any point already has one of its squares
                    # (at most 4) used.
                    is_taken = False
                    square = range(4)
                    for i in range(4):
                        # compute the position of the point in relation to the
                        # middle corresponding to one of the following squares
                        # position: [(1,1), (-1,1), (1,-1), (-1,-1)]
                        vx = middle_x - points[i].x
                        vy = middle_y - points[i].y

                        square[i] = (int(vx/abs(vx)), int(vy/abs(vy)))

                        belongs = square[i] in squares_taken[points[i]]

                        is_taken = is_taken or belongs

                    if not is_taken:

                        cell = LTComponent((point.x, point.y,
                                            intersection[0].x, intersection[0].y))

                        cells.add(cell)

                        for i in range(4):
                            squares_taken[points[i]].add(square[i])
                        break

        return cells

    def _build_elements(self, cells):
        """
        Converts the cells into elements.
        """
        elements = []
        for cell in cells:
            elements.append(self.Element(cell))

        for row in reversed(self._rows_borders[:-1]):
            for column in self._columns_borders[:-1]:
                for cell_index, cell in enumerate(cells):
                    if cell.y0 < row + 0.1 < cell.y1 and\
                       cell.x0 < column + 0.1 < cell.x1:
                        elements[cell_index].add(row, column)

        return sorted(elements, key=lambda e: (e.cell.x0, e.cell.y0))

    @property
    def cells(self):
        return self._cells

    def add(self, item):
        """
        Adds a text item to the table, inserting it into the correct cell.
        """
        for element in self._elements:
            if element.cell.is_hoverlap(item) and element.cell.is_voverlap(item):
                element.add_line(item, element.cell.bbox)
                break

    def as_html(self):

        string = ''
        for row in reversed(self._rows_borders[:-1]):
            string += '<tr>\n'
            for column in self._columns_borders[:-1]:
                for element in self._elements:
                    if element.column == column and element.row == row:

                        lines = element.lines
                        colspan = element.colspan
                        rowspan = element.rowspan

                        text = '\n'.join(line.as_html() for line in lines)

                        if colspan:
                            colspan = 'colspan="%d"' % (colspan + 1)
                        else:
                            colspan = ''

                        if rowspan:
                            rowspan = 'rowspan="%d"' % (rowspan + 1)
                        else:
                            rowspan = ''

                        attributes = ''
                        if rowspan or colspan:
                            attributes = ' '
                        if rowspan and colspan:
                            attributes += rowspan + ' ' + colspan
                        else:
                            attributes += rowspan + colspan

                        string += '<td%s>%s</td>\n' % (attributes, text)
            string += '</tr>\n'
        return '<table>\n%s</table>' % string


class BlockquoteStart(object):

    def as_html(self):
        return '<blockquote>'


class BlockquoteEnd(object):

    def as_html(self):
        return '</blockquote>'


class SimpleImage(LTImage):

    def __init__(self, ltimage):
        assert(isinstance(ltimage, LTImage))
        LTComponent.__init__(self, ltimage.bbox)
        self._name = ltimage.name
        self._stream = ltimage.stream

    def as_html(self):
        return '<p>(Ver imagem no documento original.)</p>'
