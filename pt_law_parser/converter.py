# coding=utf-8
from collections import defaultdict

from pdfminer.layout import LTContainer, LTTextGroup, LAParams, LTLine, LTRect
from pdfminer.converter import PDFLayoutAnalyzer
from pdfminer.utils import apply_matrix_pt

from pt_law_parser.layout import LTNetwork, LTTextHeader, LTTextColumn
from pt_law_parser.point import Point
from pt_law_parser.html import Line, Header, Table
from pt_law_parser.meta import Meta
from pt_law_parser.auxiliar import eq, int_round, middle_x


HEADER_MIN_Y = 775
MIDDLE_X1 = (292 + 306.0)/2


class LawConverter(PDFLayoutAnalyzer):
    """
    The main parser of a page. It is a state machine between pages, and
    is able to parse a single page.
    """

    PARAGRAPH_SPACE = 11.34
    CITING_SPACE = 11.34

    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFLayoutAnalyzer.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)

        # attributes result of the parsing
        self.meta = Meta()
        self._titles = []

        # intermediary results
        self._result_lines = []

        # attributes reset on each new page
        self._tables = []
        self._networks_layouts = []
        self._network = LTNetwork()  # network of all links and nodes of tables.

        # state of the device across pages
        self.previous_line = None
        self._is_citing = False

    @property
    def titles(self):
        return self._titles

    @property
    def tables(self):
        return self._tables

    def as_html(self):

        meta = u'<meta http-equiv="Content-Type" ' \
               u'content="text/html; ' \
               u'charset=UTF-8">'
        head = u'<head>\n{meta}\n</head>\n'.format(meta=meta)

        body = u''.join(u'%s\n' % line.as_html() for line in self._result_lines)

        return u'<html>\n{head}<body>\n{body}</body>\n</html>\n'.format(
            header=u'<html>\n<head>\n', head=head, body=body)

    @property
    def result(self):
        return self._result_lines

    @property
    def center_offset(self):
        if self.meta.version == 1:
            # titles are not exactly on columns center. Obtained by testing.
            return 1.4
        elif self.meta.version == 2:
            return 0

    def is_paragraph(self, line, column):
        """
        Checks if line is a new paragraph
        """
        is_paragraph = eq(line.x0 - (column.x0 + self.citing_space),
                          self.PARAGRAPH_SPACE, 1)

        if self.meta.version == 1:
            return is_paragraph
        else:
            is_sub_paragraph = eq(line.x0 - (column.x0 + self.citing_space),
                                  2*self.PARAGRAPH_SPACE - 1, 1)

            return is_paragraph or is_sub_paragraph

    def _is_text(self, line, column):
        """
        Special conditions to exclude text that is similar to a title.
        """
        if self.meta.version == 1:
            return False

        previous_is_sub_paragraph = eq(self.previous_line.x0 -
                                       (column.x0 + self.citing_space),
                                       2*self.PARAGRAPH_SPACE - 1, 1)
        previous_is_sub_line = eq(self.previous_line.x0 -
                                  (column.x0 + self.citing_space),
                                  3*self.PARAGRAPH_SPACE, 1)

        is_sub_line = eq(line.x0 - (column.x0 + self.citing_space),
                         3*self.PARAGRAPH_SPACE, 1)

        return (previous_is_sub_paragraph or previous_is_sub_line) and \
            is_sub_line

    @staticmethod
    def is_page_centered(line):
        return line.x0 < MIDDLE_X1 < line.x1

    def is_column_centered(self, line, column):
        """
        Checks if line is centered (i.e. a section title, etc.)
        """
        return eq(middle_x(column.bbox) - self.center_offset + self.citing_space,
                  middle_x(line.bbox), 2)

    def is_full_width(self, line, column):
        return eq(line.width + self.citing_space, column.width, 3)

    def is_title(self, line, column):
        is_full_width = self.is_full_width(line, column)

        return (self.is_column_centered(line, column) and
                not (is_full_width or self.is_paragraph(line, column)) and
                not self._is_text(line, column)) or 'Bold' in line[0].fontname

    @property
    def citing_space(self):
        return self._is_citing*self.CITING_SPACE

    def add(self, element):
        self._result_lines.append(element)

    def add_header(self, line):
        self.add(Header(line.get_text()))
        self._titles.append(line)

    def add_paragraph(self, line):
        self.add(Line(line.get_text()))

    def add_table(self, table):
        if table not in self._result_lines:
            self.add(table)

    def merge(self, line):
        self._result_lines[-1].merge(Line(line.get_text()))

    def _parse_line(self, line, column):
        # todo: parse italics inside sentences

        # ignores empty lines, a by-product of the PDFMiner.
        if line.get_text().replace(' ', '') == '':
            return

        # check if text is inside table.
        for table in self._tables:
            if table.hoverlap(line) and table.voverlap(line):
                table.add(line)
                return
            elif line.y0 < table.y0 and not table.voverlap(line):
                self.add_table(table)

        if self.is_page_centered(line):
            # is only a title if not a normal line in a full page
            # (which we test since the text belongs to the left column)
            if self.is_paragraph(line, column):
                self.add_paragraph(line)
            else:
                self.add_header(line)
        elif line == self.previous_line:
            if self.is_title(line, column):
                self.add_header(line)
            else:
                self.add_paragraph(line)
        elif self.is_starting_cite(line, column):
            # a start citing is always a title (and is not always centered.)
            self.add_header(line)

        elif self.is_title(line, column):
            is_column_jump = self.previous_line.x1 < MIDDLE_X1 < line.x1
            is_page_jump = line.x1 < MIDDLE_X1 < self.previous_line.x1

            if self.is_title(self.previous_line, column) and \
                    self.previous_line.y0 - line.y1 < 0 and not \
                    (is_column_jump or is_page_jump):
                self.merge(line)
            else:
                self.add_header(line)
        else:
            # is_text = not self.is_title(line, column)
            if self.is_paragraph(line, column) or \
                    self.is_title(self.previous_line, column):
                self.add_paragraph(line)
            else:
                self.merge(line)

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

    def _is_summary_page(self, items):
        # todo: this is too broad. Make it more restrict.
        for rectangle in [item for item in items if isinstance(item, LTRect)]:
            # if is centered but not on the bottom of the page.
            if self.is_page_centered(rectangle) and not rectangle.y1 < 80:
                return True

        if len(items) <= 3:
            return False
        items = list(reversed(items[3:]))

        # the summary pages have a rectangle and a line
        line1 = None
        line2 = None
        rect = None

        if isinstance(items[0], LTRect):
            rect = items[0]
        elif isinstance(items[0], LTLine):
            line1 = items[0]
            if isinstance(items[1], LTLine):
                line2 = items[1]
                rect = items[2]
            else:
                rect = items[1]

        if rect is None or line1 is None:
            return False
        # from here on, we are in summary page.
        # let's just make sure:

        assert(eq(rect.x1, line1.x0, 1))
        if line2 is not None:
            assert(eq(rect.x1, line2.x0, 1))

        # set line1 to be always above line2
        if line2 and line2.y0 > line1.y0:
            line1, line2 = line2, line1

        # if the line1 is up, it is the first page of the summary pages
        if eq(rect.y1, line1.y0, 1):
            # first page summary
            if line2 and eq(rect.y0, line2.y0, 1):
                # one page summary
                pass
        # if the line1 is down, it is the last page of the summary pages
        if eq(rect.y0, line1.y0, 1):
            # last page summary
            pass
        return True

    def receive_layout(self, ltpage):

        # checks if we are in a summary page
        items = [item for item in ltpage if not isinstance(item, LTNetwork)]
        if self._is_summary_page(items):
            return

        # empty page
        if len(ltpage) == 0:
            return

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
            try:
                table = Table(network)
                self._tables.append(table)
            except Table.EmptyTableError:
                pass

        header = ltpage[0]
        left_column = ltpage[1]
        right_column = ltpage[2]

        self.meta.parse_header(header)
        self._parse_column(left_column)
        self._parse_column(right_column)

        # if tables are in the end of the page, write them now.
        for table in self._tables:
            self.add_table(table)

    def _parse_column(self, column):
        for line in column:
            if self.previous_line is None:  # if first item
                self.previous_line = line

            if self.is_starting_cite(line, column):
                self._is_citing = True

            self._parse_line(line, column)

            if self.is_end_cite(line):
                self._is_citing = False

            self.previous_line = line

    def is_starting_cite(self, line, column):
        return not self.is_full_width(line, column) and \
            line[0].get_text() == u'«' and u'»' not in line.get_text()

    @staticmethod
    def is_end_cite(line):
        return line[-1].get_text() == u'»'

    def _paint_network(self, path):
        network = LTNetwork()

        previous_element = None
        for tuple in path:
            if len(tuple) == 3:
                state, x, y = tuple
                element = (x, y)
                element = apply_matrix_pt(self.ctm, element)
                element = int_round(element[0]), int_round(element[1])
                element = Point(element)
            elif len(tuple) == 1 and tuple[0] == 'h':
                element = previous_element
                state = 'l'
            else:
                raise IndexError

            network.add(element)

            # state 'l' is to draw a line, which means that we have link.
            # Otherwise, we only have the point.
            if state == 'l':
                network.add_link(element, previous_element)

            previous_element = element
        self.cur_item.add(network)

    def paint_path(self, gstate, stroke, fill, evenodd, path):
        """
        Creates a LTNetwork out of the different drawing elements.
        """

        # ignore lines above header
        if path[0][0] in 'lm' and path[0][2] > HEADER_MIN_Y - 5:
            return

        path_string = ''.join(x[0] for x in path)

        # ignore curves
        if 'c' in path_string:
            return

        # a rectangle is never part of a table, parse it as other.
        if path_string == 'mlllh':
            return PDFLayoutAnalyzer.paint_path(self, gstate, stroke, fill,
                                                evenodd, path)
        # a line is parsed both as a line and as part of a network.
        elif path_string == 'ml':
            PDFLayoutAnalyzer.paint_path(self, gstate, stroke, fill,
                                         evenodd, path)
        # this situation may occur on the first page of the PDF; we thus
        # set it here explicitly.
        elif path_string == 'mlml':
            PDFLayoutAnalyzer.paint_path(self, gstate, stroke, fill,
                                         evenodd, path[:2])
            PDFLayoutAnalyzer.paint_path(self, gstate, stroke, fill,
                                         evenodd, path[2:])

        # ignore (non-rectangle) filled stuff
        if fill:
            return

        self._paint_network(path)


class LAOrganizer(LAParams):

    def __init__(self):
        # 0.25: relative overlap between lines
        LAParams.__init__(self, line_overlap=0.25, line_margin=0.1, boxes_flow=0,
                          char_margin=2)

    @staticmethod
    def _organize_header(header, lines):
        while lines[0].y0 > HEADER_MIN_Y:
            header.add(lines.pop(0))

        return lines

    @staticmethod
    def _last_page_limit(items):
        """
        Returns the y of the line that ends the last page.
        """
        items = [item for item in items if isinstance(item, LTLine)]
        items.sort(key=lambda item: item.y0)

        if len(items) >= 2 and LawConverter.is_page_centered(items[1]) and \
                items[0].x0 > MIDDLE_X1:
            return items[1].y0
        else:
            return 0

    def group_textlines(self, bbox, lines, other_objs):
        header = LTTextHeader()
        left_column = LTTextColumn()
        right_column = LTTextColumn()

        lines = self._organize_header(header, lines)

        last_page_limit = self._last_page_limit(other_objs)

        for line in lines:
            assert(line.y0 < HEADER_MIN_Y)  # assert it is not on the header

            # ignores lines below the end
            if line.y0 <= last_page_limit:
                continue

            if line.x0 < MIDDLE_X1:
                left_column.add(line)
            else:
                right_column.add(line)

        return [header, left_column, right_column]

    def group_textboxes(self, bbox, boxes, other_objs):
        group = LTTextGroup(boxes)
        return [group]
