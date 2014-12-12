# coding=utf-8
from pdfminer.layout import LTContainer, LTTextGroup, LAParams, LTLine, LTRect, \
    LTFigure
from pdfminer.converter import PDFLayoutAnalyzer
from pdfminer.utils import apply_matrix_pt

from pt_law_parser.layout import LTNetwork, LTTextHeader, LTTextColumn
from pt_law_parser.point import Point
from pt_law_parser.html import Line, Header, Table, SimpleImage, BlockquoteEnd, \
    BlockquoteStart
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
                     2002: 0}

    # (8.1992, 6.123) => small letters have smaller paragraph space.
    _PARAGRAPH_SPACE = {None: (11.34, 8.1992),
                        2002: (10.668, 21.958, 31.98),
                        'v2': (11.34, 6.123, 8.1992, 20.93)}

    _CENTER_OFFSET = {None: (1.4,),
                      'v2': (0,), 2013: (1.4, -5.33)}

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
        return self._get_parameters(meta, self._PARAGRAPH_SPACE)

    def is_paragraph(self, meta, line, no_paragraph_x0):
        is_paragraph = False
        for paragraph_space in self._paragraph_spaces(meta):
            is_paragraph = is_paragraph or \
                eq(line.x0 - no_paragraph_x0, paragraph_space, 2)

        return is_paragraph

    def _center_offsets(self, meta):
        return self._get_parameters(meta, self._CENTER_OFFSET)

    def is_column_centered(self, meta, line, center_x):
        """
        Checks if line is centered (i.e. a section title, etc.)
        """
        is_centered = False
        for center_offset in self._center_offsets(meta):
            is_centered = is_centered or \
                eq(center_x - center_offset, middle_x(line.bbox), 2)
        return is_centered


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

    def is_paragraph(self, line, column):
        """
        Checks if line is a new paragraph
        """
        no_paragraph_x0 = column.x0 + self.citing_space
        return self._parameters.is_paragraph(self.meta, line, no_paragraph_x0)

    def _is_text(self, line, column):
        """
        Special conditions to exclude what is text but would otherwise be
        interpreted as a title.
        """
        # todo: send this code logic to the ConverterParameters
        if self.meta.version == 1:
            return False

        paragraph_space = 11.34
        previous_is_sub_paragraph = eq(self.previous_line.x0 -
                                       (column.x0 + self.citing_space),
                                       2*paragraph_space - 1, 1)
        previous_is_sub_line = eq(self.previous_line.x0 -
                                  (column.x0 + self.citing_space),
                                  3*paragraph_space, 1)

        is_sub_line = eq(line.x0 - (column.x0 + self.citing_space),
                         3*paragraph_space, 1)

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
        return self._parameters.is_column_centered(self.meta, line, center_x)

    def is_full_width(self, line, column):
        return eq(line.width + self.citing_space, column.width, 3)

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
        self.add(Line(line.get_text()))

    def add_table(self, table):
        if table not in self._result_lines:
            self.add(table)

    def add_image(self, image):
        if image not in self._result_lines:
            self.add(image)

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
            elif line.y0 < table.y0 and table.hoverlap(line) and \
                    not table.voverlap(line):
                self.add_table(table)

        # check if there is an image that we need to add.
        for image in self._images:
            if line.y0 < image.y0 and image.hoverlap(line) and \
                    not image.voverlap(line):
                self.add_image(image)

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

    def _is_summary_page(self, items):
        # todo: this is too broad. Make it more restrict.
        rectangles = [item for item in items if isinstance(item, LTRect)]

        for rectangle in rectangles:
            # if is centered but not on the bottom of the page.
            if self.is_page_centered(rectangle) and not rectangle.y1 < 80:
                return True

        if not rectangles:
            return False

        if len(items) <= 3:
            return False

        # ignore header and 2 columns.
        items = list(sorted(items[3:], key=lambda x: (x.x0, x.y0)))

        if not isinstance(items[0], LTRect):
            return False
        # some layouts have a rectangle too much.
        if isinstance(items[1], LTRect):
            items.pop(1)

        # situation where we have a left-rectangle, summary
        if eq(items[0].x0, 50, 2) and eq(items[0].x1, 169.512, 2):
            return True
        else:
            return False

    def _create_tables(self, ltpage):
        self._tables = []
        _network = LTNetwork()

        def merge_networks(item):
            """
            Recursively merges all `LTNetwork` instances into a single
            `LTNetwork`, `_network`.
            """
            if isinstance(item, LTNetwork):
                for point in item.points:
                    _network.add(point)
                    for link in item.links[point]:
                        _network.add(link)
                        _network.add_link(point, link)
            if isinstance(item, LTContainer):
                for child in item:
                    merge_networks(child)

        merge_networks(ltpage)

        networks = _network.create_components()

        # creates tables from networks.
        for network in networks:
            try:
                table = Table(network)
                self._tables.append(table)
            except Table.EmptyTableError:
                pass

    def receive_layout(self, ltpage):

        # checks if we are in a summary page
        items = [item for item in ltpage if not isinstance(item, LTNetwork)]
        if self._is_summary_page(items):
            return

        # empty page (no header or empty left column)
        if len(ltpage) < 3 or not isinstance(ltpage[0], LTTextHeader) or \
                not len(ltpage[1]):
            return

        self._images = [SimpleImage(item[0]) for item in ltpage
                        if isinstance(item, LTFigure)]

        self._create_tables(ltpage)

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
                self.add(BlockquoteStart())

            self._parse_line(line, column)

            if self.is_end_cite(line):
                if self._is_citing:
                    self.add(BlockquoteEnd())
                self._is_citing = False

            self.previous_line = line

        # if missing tables are aligned with column, write them now.
        for table in self._tables:
            if table.hoverlap(column) and table.voverlap(column):
                self.add_table(table)

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

    @staticmethod
    def _last_page_limit(items):
        """
        Returns the y of the line that ends the last page.
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
        elif len(lines) >= 4 and crosses_middle(lines[3]) and \
                lines[0].x0 < MIDDLE_X1 and lines[1].x0 < MIDDLE_X1:
            return lines[2].y0
        else:
            return 0

    def group_textlines(self, bbox, lines, other_objs):
        header = LTTextHeader()
        left_column = LTTextColumn()
        right_column = LTTextColumn()

        header_min_y = lines[0].y0 - 5

        last_page_limit = self._last_page_limit(other_objs)

        for line in lines:
            if line.y0 > header_min_y:
                header.add(line)
                continue

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
