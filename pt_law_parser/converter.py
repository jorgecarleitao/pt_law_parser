# coding=utf-8
from pdfminer.layout import LTTextGroup, LAParams, LTLine, LTRect, LTFigure, \
    LTTextBox
from pdfminer.converter import PDFLayoutAnalyzer
from pdfminer.utils import apply_matrix_pt

from pt_law_parser.layout import LTNetwork, LTTextHeader, LTTextColumn
from pt_law_parser.point import Point
from pt_law_parser.html import Paragraph, Header, Table, SimpleImage, \
    BlockquoteStart, BlockquoteEnd
from pt_law_parser.meta import Meta
from pt_law_parser.auxiliar import eq, int_round, middle_x


HEADER_MIN_Y = 775
MIDDLE_X1 = (292 + 306.0)/2


def crosses_middle(line):
    return line.x0 < MIDDLE_X1 < line.x1


class ConverterParameters(object):
    """
    This class is responsible for providing document-dependent parameters.

    It contains parameters (e.g. citing spaces), and returns them depending on
    the meta information provided to it.
    """
    # None represents the default value.
    _CITING_SPACE = {None: 11.34,
                     2002: 0,
                     1998: 0}

    _PARAGRAPH_SPACE = {None: (11.34,),
                        2002: (10.668,),
                        # (8.1992) -> line advance in paragraph of center column.
                        1997: (11.34, 8.2),
                        'v2': (11.34,)}

    # space created by bullets.
    _SUBPARAGRAPH_SPACE = {None: tuple(),
                           2002: (16.96, 21.958, 31.98),
                           'v2': (20.93, 31.985)}

    _SUB_LINE_SPACE = {None: tuple(),
                       2002: (29.48, 34.843),
                       'v2': (34.844, 31.98)}

    @staticmethod
    def _get_parameters(meta, parameters_dict):
        """
        Internal method that maps a meta into a specific list of parameters
        """
        if meta.year in parameters_dict:
            return parameters_dict[meta.year]
        elif 'v%d' % meta.version in parameters_dict:
            return parameters_dict['v%d' % meta.version]
        else:
            return parameters_dict[None]

    def citing_space(self, meta):
        return self._get_parameters(meta, self._CITING_SPACE)

    def _paragraph_spaces(self, meta):
        return self._get_parameters(meta, self._PARAGRAPH_SPACE) +\
            self._get_parameters(meta, self._SUBPARAGRAPH_SPACE)

    def is_paragraph(self, meta, line, no_paragraph_x0):
        is_paragraph = False
        for paragraph_space in self._paragraph_spaces(meta):
            is_paragraph = is_paragraph or \
                eq(line.x0 - no_paragraph_x0, paragraph_space, 2)

        return is_paragraph

    def is_subparagraph(self, meta, line, no_paragraph_x0):
        is_sub_paragraph = False
        for space in self._get_parameters(meta, self._SUBPARAGRAPH_SPACE):
            is_sub_paragraph = is_sub_paragraph or \
                eq(line.x0 - no_paragraph_x0, space, 2)
        return is_sub_paragraph

    def is_subparagraph_line(self, meta, line, no_paragraph_x0):
        is_sub_line = False
        for space in self._get_parameters(meta, self._SUB_LINE_SPACE):
            is_sub_line = is_sub_line or \
                eq(line.x0 - no_paragraph_x0, space, 2)
        return is_sub_line

    @staticmethod
    def right_column_x(meta):
        data = {2014: (306, 547.4),
                2013: (306, 547.4),
                2012: (306, 547.4),
                2010: (306, 547.4),
                2002: (301.178, 540.1),
                2001: (301.178, 540.1),
                2000: (301.178, 540.1),
                1999: (301.178, 540.1),
                1998: (315.344, 554.144),
                1997: (303, 533),
                }
        if meta.year in data:
            return data[meta.year]
        else:
            return 306, 547.4

    @staticmethod
    def left_column_x(meta):
        data = {2014: (50.26, 291.74),
                2013: (50.26, 291.74),
                2012: (50.26, 291.74),
                2010: (50.26, 291.74),
                2002: (45.34, 284.14),
                2001: (45.34, 284.14),
                2000: (45.34, 284.14),
                1999: (45.34, 284.14),
                1998: (59.528, 298.278),
                1997: (57.65, 286.95),
                }
        if meta.year in data:
            return data[meta.year]
        else:
            return 50.26, 291.74


class LawConverter(PDFLayoutAnalyzer):
    """
    The main parser of a page. It is a state machine between pages, and
    is able to parse a single page.
    """
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFLayoutAnalyzer.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)

        self._parameters = ConverterParameters()

        # attributes result of the parsing
        self.meta = Meta()
        self._titles = []
        self._all_tables = []

        # intermediary results
        self._result_lines = []

        # attributes reset on each new page
        self._tables = []
        self._images = []

        # state of the device across pages
        self.previous_line = None
        self._is_citing = False

    @property
    def titles(self):
        return self._titles

    @property
    def paragraphs(self):
        return [p for p in self._result_lines if isinstance(p, Paragraph) and not
                isinstance(p, Header)]

    @property
    def tables(self):
        return self._all_tables

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

    def is_paragraph(self, line, column):
        """
        Checks if line is a new paragraph
        """
        no_paragraph_x0 = column.x0 + self.citing_space
        return self._parameters.is_paragraph(self.meta, line, no_paragraph_x0) and\
            not self.is_line(line, column)

    def is_line(self, line, column):
        """
        Special condition to distinguish a line from a paragraph.
        """
        return self._is_text(line, column) and \
            0 < line.y1 - self.previous_line.y0 < 2

    def _is_text(self, line, column):
        """
        Special conditions to exclude what is text but would otherwise be
        interpreted as a title.
        """
        previous_is_sub_paragraph = self._parameters.is_subparagraph(
            self.meta, self.previous_line, column.x0 + self.citing_space)

        previous_is_sub_line = self._parameters.is_subparagraph_line(
            self.meta, self.previous_line, column.x0 + self.citing_space)

        is_sub_line = self._parameters.is_subparagraph_line(
            self.meta, line, column.x0 + self.citing_space)

        return (previous_is_sub_paragraph or previous_is_sub_line) and \
            is_sub_line

    @staticmethod
    def is_page_centered(line):
        return crosses_middle(line)

    def is_column_centered(self, line, column):
        """
        Checks if line is centered (i.e. a section title, etc.)
        """
        center_x = middle_x(column.bbox) + self.citing_space
        return eq(center_x, middle_x(line.bbox), 2)

    def is_full_width(self, line, column):
        return eq(line.width + self.citing_space, column.width, 4)

    def is_title(self, line, column):
        is_full_width = self.is_full_width(line, column)

        return (self.is_column_centered(line, column) and
                not (is_full_width or self.is_paragraph(line, column)) and
                not self._is_text(line, column)) or 'Bold' in line[0].fontname

    @property
    def citing_space(self):
        return self._parameters.citing_space(self.meta)*self._is_citing

    def add(self, element):
        self._result_lines.append(element)

    def add_header(self, line):
        self.add(Header(line.get_text()))
        self._titles.append(line)

    def add_paragraph(self, line):
        self.add(Paragraph(line.get_text()))

    def add_table(self, table):
        if table not in self._result_lines:
            self.add(table)

    def add_image(self, image):
        if image not in self._result_lines:
            self.add(image)

    def merge(self, line):
        self._result_lines[-1].merge(Paragraph(line.get_text()))

    def _parse_line(self, line, column):
        # todo: parse italics inside sentences

        if line == self.previous_line:
            if self.is_title(line, column):
                self.add_header(line)
            else:
                self.add_paragraph(line)
        elif self.is_starting_cite(line, column):
            # a start citing is always a title (and is not always centered.)
            self.add_header(line)

        elif self.is_title(line, column):
            is_column_jump = self.previous_line not in column

            if self.is_title(self.previous_line, column) and \
                    self.previous_line.y0 - line.y1 < 0 and not \
                    is_column_jump:
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

    @staticmethod
    def _last_page_limit(items):
        """
        Computes the y that separates irrelevant content of the last page from
        relevant one.
        """
        rectangles = [item for item in items if isinstance(item, LTRect)]
        lines = [item for item in items if isinstance(item, LTLine)]
        lines.sort(key=lambda item: item.y0)
        rectangles.sort(key=lambda item: item.y0)

        # documents from 2012-2014 have a single thicker line.
        if lines and rectangles and \
                lines[0].linewidth == 1 and lines[0].x0 == rectangles[0].x0 and\
                lines[0].x1 == rectangles[0].x1:
            return lines[0].y0

        if len(lines) >= 2 and crosses_middle(lines[1]) and \
                lines[0].x0 > MIDDLE_X1:
            return lines[1].y0
        # documents from 1997
        elif len(rectangles) > 1 and eq(rectangles[1].y1, 381.590, 2):
            return 381.590
        else:
            return 0

    def _is_summary_page(self, items):
        # todo: this is too broad. Make it more restrict.
        items = [item for item in items if isinstance(item, (LTRect, LTLine))]
        items = sorted(items, key=lambda x: (x.x0, x.y0))
        rectangles = [item for item in items if isinstance(item, LTRect)]

        if not rectangles:
            return False

        for rectangle in rectangles:
            # if is centered but not on the bottom of the page.
            if self.is_page_centered(rectangle) and not rectangle.y1 < 80:
                return True

        # summary page always contains items
        if len(items) <= 1:
            return False

        if not isinstance(items[0], LTRect):
            return False
        # some layouts have a rectangle too much.
        if isinstance(items[1], LTRect):
            items.pop(1)

        # situation where we have a left-rectangle in summary page
        if eq(items[0].x0, 50, 2) and eq(items[0].x1, 169.512, 2):
            return True
        else:
            return False

    def _create_tables(self, items):
        self._tables = []
        _network = LTNetwork()

        # merge all LTNetworks in a single network _network.
        for item in items:
            if isinstance(item, LTNetwork):
                for point in item.points:
                    _network.add(point)
                    for link in item.links[point]:
                        _network.add(link)
                        _network.add_link(point, link)

        networks = _network.create_components()

        # creates tables from networks.
        for network in networks:
            try:
                table = Table(network)
                self._tables.append(table)
                self._all_tables.append(table)
            except Table.EmptyTableError:
                pass

    def _build_components(self, lines, header_min_y, last_page_limit):
        header = LTTextHeader()
        center_column = LTTextColumn()
        left_column = LTTextColumn()
        right_column = LTTextColumn()

        def add_to_column(item):
            if item.y0 <= last_page_limit:
                pass  # ignores lines below the end
            elif item.x0 < item.x1 < MIDDLE_X1:
                left_column.add(item)
            elif MIDDLE_X1 < item.x0 < item.x1:
                right_column.add(item)
            else:
                center_column.add(item)

        def in_table(line):
            # check if text is inside table.
            for table in self._tables:
                if table.hoverlap(line) and table.voverlap(line):
                    table.add(line)
                    return True
            return False

        # add the tables to respective columns
        for table in self._tables:
            add_to_column(table)

        previous_line = None
        for line in lines:
            assert(line._objs[-1].get_text() == '\n')
            line._objs = line._objs[:-1]  # remove '\n' char from line.

            # ignores empty lines, a by-product of the PDFMiner.
            if line.get_text().replace(' ', '') == '':
                continue

            if line.y0 > header_min_y - 5:  # -5: a small margin for variations
                header.add(line)
            elif line.y0 <= last_page_limit:
                pass  # ignores lines below the end
            elif in_table(line):
                pass
            else:
                if line.x0 < line.x1 < MIDDLE_X1:

                    is_below = len(left_column) and len(center_column)
                    is_below = is_below and \
                        left_column.y0 > center_column.y0 > line.y0

                    # a line that is in center column, but finishes before
                    # MIDDLE_X1; OR a line already inside the center column; OR
                    # left_column is above center which is above line.
                    if previous_line in center_column and \
                            previous_line.y0 - line.y1 < 0 or \
                            center_column.voverlap(line) and \
                            center_column.hoverlap(line) or \
                            is_below:
                        center_column.add(line)
                    else:
                        left_column.add(line)
                elif MIDDLE_X1 < line.x0 < line.x1:
                    right_column.add(line)
                else:
                    center_column.add(line)
            previous_line = line

        # add images to respective columns
        for image in self._images:
            add_to_column(image)

        if len(center_column) and len(left_column):
            assert(not (center_column.voverlap(left_column) and
                   center_column.hoverlap(left_column)))
        # sort inside components
        header.analyze(None)
        left_column.analyze(None)
        right_column.analyze(None)
        center_column.analyze(None)
        return header, center_column, left_column, right_column

    def receive_layout(self, ltpage):
        if not len(ltpage) or not isinstance(ltpage[0], LTTextBox):
            # No text => ignore.
            return
        lines = ltpage[0]
        items = ltpage[1:]

        # summary page => ignore.
        if self._is_summary_page(items):
            return

        # the y0 which defines the limit of content of a last page
        last_page_limit = self._last_page_limit(items)

        header_min_y = lines[0].y0

        # header is below the last page limit => empty last page => ignore.
        if last_page_limit > header_min_y:
            return

        self._images = [SimpleImage(item[0]) for item in items
                        if isinstance(item, LTFigure)]
        self._create_tables(items)

        header, center_column, left_column, right_column = \
            self._build_components(lines, header_min_y, last_page_limit)

        if len(left_column) == 0 and len(center_column) == 0:
            # Page with no content => ignore.
            return

        self.meta.parse_header(header)

        left_column.expand_left(self._parameters.left_column_x(self.meta)[0])
        left_column.expand_right(self._parameters.left_column_x(self.meta)[1])
        right_column.expand_left(self._parameters.right_column_x(self.meta)[0])
        right_column.expand_right(self._parameters.right_column_x(self.meta)[1])

        if center_column.y0 < left_column.y0:
            c1 = left_column
            c2 = right_column
            c3 = center_column
        else:
            c1 = center_column
            c2 = left_column
            c3 = right_column

        self._parse_column(c1)
        self._parse_column(c2)
        self._parse_column(c3)

    def _parse_column(self, column):
        for line in column:
            if isinstance(line, Table):
                self.add_table(line)
                continue
            if isinstance(line, SimpleImage):
                self.add_image(line)
                continue

            if self.previous_line is None:  # if first item
                self.previous_line = line

            if self.is_starting_cite(line, column):
                self._is_citing = True
                self.add(BlockquoteStart())

            self._parse_line(line, column)

            if self.is_end_cite(line):
                if self._is_citing:
                    self.add(BlockquoteEnd())
                self._is_citing = False

            self.previous_line = line

    def is_starting_cite(self, line, column):
        return not self.is_full_width(line, column) and \
            not self.is_paragraph(line, column) and \
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

    def group_textlines(self, bbox, lines, other_objs):
        box = LTTextBox()
        for line in lines:
            box.add(line)
        return [box]

    def group_textboxes(self, bbox, boxes, other_objs):
        group = LTTextGroup(boxes)
        return [group]
