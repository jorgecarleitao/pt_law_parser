# coding=utf-8
import datetime


MONTH_NAME_TO_MONTH = {
    'janeiro': 1,
    'fevereiro': 2,
    'março': 3,
    'maio': 4,
    'abril': 5,
    'junho': 6,
    'julho': 7,
    'agosto': 8,
    'setembro': 9,
    'outubro': 10,
    'novembro': 11,
    'dezembro': 12}

ROMAN_TO_NUMBER = {'I': 1,
                   'II': 2}


class Meta(object):
    def __init__(self):
        # suplementary information has a page associated to it.
        self._suplement_page = None
        self._pages = []
        self._series = 0
        self._number = 0
        self._date = datetime.date(1980, 1, 1)
        self._document_version = 0

    def set_header_info(self, series, number, date):
        if self._series == 0:
            self._series = series
            self._number = number
            self._date = date
        else:
            assert(self._series == series)
            assert(self._number == number)
            assert(self._date == date)

    def add_page(self, page):
        try:
            page = int(page)
        except ValueError:
            numbers = page.split('-')
            self._suplement_page = int(numbers[0])
            page = int(numbers[1].strip()[1:-1])

        assert(isinstance(page, int))
        assert(page not in self._pages)
        if self._pages:
            assert(page == self._pages[-1] + 1)
        self._pages.append(page)

    @staticmethod
    def _build_date(piece):
        piece = piece.split(' de ')
        month = MONTH_NAME_TO_MONTH[piece[1].lower().strip()]
        return datetime.date(int(piece[2]), month, int(piece[0]))

    def _parse_header_v1(self, header):
        """
        Parses the header of documents posterior to ~2006.
        """
        if 'BoldMT' in header[0][0].fontname:
            page_no = header[0].get_text()
            document_identifier = header[1].get_text().strip()
        else:
            page_no = header[1].get_text()
            document_identifier = header[0].get_text().strip()

        self.add_page(page_no)

        document_identifier = document_identifier.split(',')[1]
        pieces = document_identifier.split(u'—')

        # extract header info
        pieces[0] = int(pieces[0][:2])
        pieces[1] = int(pieces[1][5:-1])
        pieces[2] = self._build_date(pieces[2])

        self.set_header_info(series=pieces[0], number=pieces[1], date=pieces[2])

        self._document_version = 1

    def _parse_header_v2(self, header):
        """
        Parses the header of documents prior to ~2006.
        """
        if header[0][0].fontname == 'Dutch801BT-Roman':
            page_no = int(header[0].get_text())
            series_identifier = header[1].get_text()
            number_and_date = header[2].get_text()
        else:
            page_no = int(header[2].get_text())
            series_identifier = header[1].get_text()
            number_and_date = header[0].get_text()

        self.add_page(page_no)

        series = ROMAN_TO_NUMBER[series_identifier.split(u'—')[1]
                                 .lstrip().split(' ')[0]]

        pieces = number_and_date.split(u'—')
        number = int(pieces[0].strip().split(' ')[1])
        try:
            date = datetime.datetime.strptime(pieces[1].strip(), '%d-%m-%Y').date
        except ValueError:
            # version that uses full date.
            date = self._build_date(pieces[1])

        self.set_header_info(series, number, date)

        self._document_version = 2

    def parse_header(self, header):
        if len(header) == 2:
            self._parse_header_v1(header)
        elif len(header) == 3:
            self._parse_header_v2(header)

    @property
    def version(self):
        return self._document_version

    @property
    def pages(self):
        return self._pages
