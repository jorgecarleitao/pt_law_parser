# coding=utf-8
from collections import defaultdict

from pdfminer.layout import LTContainer, LTTextGroup, LAParams
from pdfminer.converter import PDFLayoutAnalyzer
from pdfminer.utils import apply_matrix_pt

from pt_law_parser.layout import LTNetwork, LTTextHeader, LTTextColumn
from pt_law_parser.point import Point
from pt_law_parser.html import Line, Table
from pt_law_parser.meta import Meta


HEADER_MIN_Y = 775
MIDDLE_X1 = (292 + 306.0)/2


def _ceil(x, base=1):
    return int(base * round(float(x)/base))


def eq(value1, value2, epsilon):
    return abs(value1 - value2) < epsilon


def middle_x(bbox):
    return (bbox[0] + bbox[2])/2.


class LawConverter(PDFLayoutAnalyzer):
    """
    The main parser of a page. It is a state machine between pages, and
    is able to parse a single page.
    """

    PARAGRAPH_Y_SPACE = 2  # 2 chosen by trial. Notice that lines can overlap.
    PARAGRAPH_SPACE = 11
    CITING_SPACE = 11
    EOF_EPSILON = 5  # by trial. Distance to max EOF position to considered a
    #  new paragraph.

    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFLayoutAnalyzer.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)

        # attributes result of the parsing
        self.result = ''
        self.meta = Meta()
        self._titles = []

        # intermediary results
        self._result_lines = []

        # attributes reset on each new page
        self._tables = []
        self._networks_layouts = []
        self._network = LTNetwork()  # network of all links and nodes of tables.

        #
        self.previous_line = None
        self._is_citing = False

    @property
    def titles(self):
        return self._titles

    @property
    def tables(self):
        return self._tables

    def write(self, text):
        self.result += text

    @property
    def center_offset(self):
        if self.meta.version == 1:
            # titles are not exactly on columns center. Obtained by testing.
            return 1.5
        elif self.meta.version == 2:
            return 0

    def is_paragraph(self, line, column):
        """
        Checks if line is a new paragraph
        """
        if self.meta.version == 1:
            return eq(line.x0 - (column.x0 + self.citing_space),
                      self.PARAGRAPH_SPACE, 1)
        else:
            return eq(line.x0 - (column.x0 + self.citing_space),
                      self.PARAGRAPH_SPACE, 1) or \
                eq(line.x0 - (column.x0 + self.citing_space),
                      2*self.PARAGRAPH_SPACE - 1, 1)

    @staticmethod
    def is_page_centered(line):
        return line.x0 < MIDDLE_X1 < line.x1

    def is_centered(self, line, column):
        """
        Checks if line is centered (i.e. a section title, etc.
        """
        return eq(middle_x(column.bbox) - self.center_offset +
                  self.citing_space/2.,
                  middle_x(line.bbox), 0.4) and\
            line.x0 - (column.x0 + self.citing_space) > 1 or\
            'Bold' in line[0].fontname

    @property
    def citing_space(self):
        return self._is_citing*self.CITING_SPACE

    def write_table(self, table):
        if table not in self._result_lines:
            self._result_lines.append(table)

    def write_lines(self):
        for line in self._result_lines:
            self.write('%s\n' % line.as_html())

    def add_paragraph(self, line):
        self._result_lines.append(Line(line.get_text()))

    def merge(self, line):
        self._result_lines[-1].merge(Line(line.get_text()))

    def _parse_line(self, line, column):
        # todo: parse italics inside sentences

        # check if text is inside table.
        for table in self._tables:
            if table.hoverlap(line) and table.voverlap(line):
                table.add(line)
                return
            elif line.y0 < table.y0 and not table.voverlap(line):
                self.write_table(table)

        is_centered_title = self.is_centered(line, column)

        is_paragraph_space = self.is_paragraph(line, column) or self.is_centered(
            self.previous_line, column)

        is_column_jump = self.previous_line.x1 < MIDDLE_X1 < line.x1
        is_page_jump = line.x1 < MIDDLE_X1 < self.previous_line.x1

        if self.is_page_centered(line):
            self.add_paragraph(line)
            # is only a title if not a normal line in a full page
            # (which we test since the text belongs to the left column)
            if not is_paragraph_space:
                self._titles.append(line)
        elif line == self.previous_line:
            self.add_paragraph(line)
            if is_centered_title:
                self._titles.append(line)
        elif self.is_starting_cite(line):
            self.add_paragraph(line)
            # a start citing is always a title (and is not always centered.)
            self._titles.append(line)
        elif is_centered_title:
            if self.previous_line.y0 - line.y1 < 0 and not (is_column_jump or
                                                            is_page_jump):
                self.merge(line)
            else:
                self._titles.append(line)
                self.add_paragraph(line)
        elif not is_paragraph_space:
            # merge lines
            self.merge(line)
        else:
            self.add_paragraph(line)

    def _sanitize_network(self):
        """
        Removes duplicated points close to each other.
        """
        # select points to remove by proximity
        points_to_remove = set()
        for point in self._network.points:
            for point_prime in self._network.points:
                if point != point_prime and\
                        abs(point_prime.x - point.x) <= 2 and\
                        abs(point_prime.y - point.y) <= 2 and\
                        (point_prime, point) not in points_to_remove:
                    points_to_remove.add((point, point_prime))

        removed_points = set()
        for point, point_prime in points_to_remove:
            if point in removed_points:
                continue

            for link_prime in self._network.links[point_prime]:
                self._network.links[point].add(link_prime)
                self._network.links[link_prime].add(point)
                self._network.links[link_prime].remove(point_prime)

            # track removed points
            removed_points.add(point_prime)
            self._network.remove_point(point_prime)

    def _sanitize_network1(self):
        """
        Removes nodes with only two links (are not important for table creation).
        """
        points_to_remove = set()
        for point in self._network.points:
            if len(self._network.links[point]) == 2:
                point1 = list(self._network.links[point])[0]
                point2 = list(self._network.links[point])[1]

                self._network.links[point1].remove(point)
                self._network.links[point1].add(point2)

                self._network.links[point2].add(point1)
                self._network.links[point2].remove(point)

                points_to_remove.add(point)

        for point in points_to_remove:
            self._network.remove_point(point)

    def _sanitize_layouts(self):
        """
        Makes the links horizontal/vertical by aligning nodes.
        """
        for table in self._networks_layouts:

            # make an histogram of the most common x and y values
            raw_x_values = defaultdict(int)
            raw_y_values = defaultdict(int)
            for point in table:
                raw_x_values[point.x] += 1
                raw_y_values[point.y] += 1

            # stores which values to replace (remove close values)
            replace_x = {}
            for x in raw_x_values:
                for x_prime in raw_x_values:
                    if x != x_prime and abs(x - x_prime) < 5:
                        if raw_x_values[x_prime] > raw_x_values[x]:
                            replace_x[x] = x_prime
                        else:
                            replace_x[x_prime] = x

            replace_y = {}
            for y in raw_y_values:
                for y_prime in raw_y_values:
                    if y != y_prime and abs(y - y_prime) < 5:
                        if raw_y_values[y_prime] > raw_y_values[y]:
                            replace_y[y] = y_prime
                        else:
                            replace_y[y_prime] = y

            for point in table:
                if point.x in replace_x:
                    table.replace(point, Point((replace_x[point.x], point.y)))

            for point in table:
                if point.y in replace_y:
                    table.replace(point, Point((point.x, replace_y[point.y])))

    def _build_tables(self):
        """
        Builds non-overlapping tables from overlapping tables.

        Currently is only used to build the size of the independent tables,
        but also contains all information about the table, which can be used to
        reconstruct it.
        """

        def add_point(table, point):
            """
            Recursively adds a point and respective connected component to
            table.
            """
            table.add(point)
            for link in self._network.links[point]:
                table.add_link(point, link)

            for x in self._network.links[point]:
                if x not in table:
                    add_point(table, x)

        for point in self._network.points:
            # try to find the table of this point.
            found = None
            for network in self._networks_layouts:
                if point in network:
                    found = network
                    break

            # if no table exists, create one for it.
            if found is None:
                self._networks_layouts.append(LTNetwork())
                found = self._networks_layouts[-1]

            # finally, add its connected component to the table.
            add_point(found, point)

            # asserts that the connected component is on that table only.
            for link in self._network.links[point]:
                assert(link in found)
                for network in self._networks_layouts:
                    if network != found:
                        assert(point not in network)
                        assert(link not in network)

        # asserts that we didn't lost any point
        assert(sum(len(table) for table in self._networks_layouts) ==
               len(self._network.points))

    def receive_layout(self, ltpage):
        self._tables = []
        self._networks_layouts = []
        self._network = LTNetwork()

        def merge_tables(item):
            """
            Recursively merges all `LTNetwork` instances into a single
            `LTNetwork`, `self._network`.
            """
            if isinstance(item, LTNetwork):
                for point in item.points:
                    self._network.add(point)
                    for link in item.links[point]:
                        self._network.add_link(point, link)
            if isinstance(item, LTContainer):
                for child in item:
                    merge_tables(child)

        merge_tables(ltpage)
        self._sanitize_network()
        self._sanitize_network1()
        self._build_tables()
        self._sanitize_layouts()

        # creates components with tables.
        for network in self._networks_layouts:
            self._tables.append(Table(network))

        def render(item):
            if isinstance(item, LTNetwork):
                pass
            elif isinstance(item, LTTextHeader):
                self.meta.parse_header(item)
            elif isinstance(item, LTTextColumn):
                self._parse_column(item)
            else:
                for child in item:
                    render(child)

        render(ltpage)

        for table in self._tables:
            self.write_table(table)

    def _parse_column(self, column):
        for line in column:
            if self.previous_line is None:  # if first item
                self.previous_line = line

            if self.is_starting_cite(line):
                self._is_citing = True

            self._parse_line(line, column)

            if self.is_end_cite(line):
                self._is_citing = False

            self.previous_line = line

    @staticmethod
    def is_starting_cite(line):
        # todo: this may not be enough. The end could be in the next line.
        return line[0].get_text() == u'«' and u'»' not in line.get_text()

    @staticmethod
    def is_end_cite(line):
        return line[-1].get_text() == u'»'

    def paint_path(self, gstate, stroke, fill, evenodd, path):
        """
        Creates a LTNetwork out of the different drawing elements.
        """
        network = LTNetwork()

        # ignore lines above header
        if path[0][0] in 'lm' and path[0][2] > HEADER_MIN_Y - 5:
            return

        previous_element = None
        for state, x, y in path:
            element = (x, y)
            element = apply_matrix_pt(self.ctm, element)
            element = _ceil(element[0]), _ceil(element[1])
            element = Point(element)

            network.add(element)

            # state 'l' is to draw a line, which means that we have link.
            # Otherwise, we only have the point.
            if state == 'l':
                network.add_link(element, previous_element)

            previous_element = element

        self.cur_item.add(network)


class LAOrganizer(LAParams):

    def __init__(self):
        LAParams.__init__(self, line_overlap=0, line_margin=0.1, boxes_flow=0,
                          char_margin=2)

    @staticmethod
    def _organize_header(header, lines):
        while lines[0].y0 > HEADER_MIN_Y:
            header.add(lines.pop(0))

        return lines

    def group_textlines(self, bbox, lines):
        header = LTTextHeader()
        left_column = LTTextColumn()
        right_column = LTTextColumn()

        lines = self._organize_header(header, lines)

        for line in lines:
            assert(line.y0 < HEADER_MIN_Y)  # assert it is not on the header

            if line.x0 < MIDDLE_X1:
                left_column.add(line)
            else:
                right_column.add(line)

        return [header, left_column, right_column]

    def group_textboxes(self, bbox, boxes):
        group = LTTextGroup(boxes)
        return [group]
