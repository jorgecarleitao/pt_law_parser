import unittest

from pdfminer.layout import LTComponent

from pt_law_parser.layout import LTNetwork
from pt_law_parser.html import Table
from pt_law_parser.point import Point


class LineMock(LTComponent):
    """
    A mock for LTLine.
    """
    def __init__(self, bbox, text):
        LTComponent.__init__(self, bbox)
        self._text = text

    def get_text(self):
        return self._text


class TestCase(unittest.TestCase):

    def test_a(self):
        network = LTNetwork()

        points = {Point((0, 0)), Point((1, 0)), Point((0, 1)), Point((1, 1))}
        for point in points:
            network.add(point)

        network.add_link(Point((0, 0)), Point((0, 1)))
        network.add_link(Point((0, 0)), Point((1, 0)))
        network.add_link(Point((0, 1)), Point((1, 1)))
        network.add_link(Point((1, 0)), Point((1, 1)))

        table = Table(network)

        self.assertEqual('<table>\n<tr>\n<td></td>\n</tr>\n</table>',
                         table.as_html())

    def test_b(self):
        network = LTNetwork()

        points = {Point((0, 0)), Point((9, 0)), Point((0, 9)), Point((9, 9)),
                  Point((0, 1)), Point((9, 1)), Point((1, 1)), Point((1, 9))}

        for point in points:
            network.add(point)

        network.add_link(Point((0, 0)), Point((0, 1)))
        network.add_link(Point((0, 0)), Point((9, 0)))
        network.add_link(Point((0, 1)), Point((1, 1)))
        network.add_link(Point((0, 1)), Point((0, 9)))
        network.add_link(Point((0, 9)), Point((1, 9)))
        network.add_link(Point((9, 0)), Point((9, 1)))
        network.add_link(Point((1, 1)), Point((1, 9)))
        network.add_link(Point((1, 1)), Point((9, 1)))
        network.add_link(Point((1, 9)), Point((9, 9)))
        network.add_link(Point((9, 1)), Point((9, 9)))

        table = Table(network)

        self.assertEqual(3, len(table.cells))

        expected = '<table>\n' \
                   '<tr>\n<td></td>\n<td></td>\n</tr>\n' \
                   '<tr>\n<td colspan="2"></td>\n</tr>\n' \
                   '</table>'

        self.assertEqual(expected, table.as_html())

    def test_incomplete_table(self):
        """
        Table with missing bottom border.
        """
        points = [Point((0, 8)), Point((0, 9)),
                  Point((3, 0)), Point((3, 8)), Point((3, 9)),
                  Point((5, 0)), Point((5, 8)), Point((5, 9)),
                  Point((8, 8)), Point((8, 9))]

        network = LTNetwork()
        for point in points:
            network.add(point)

        network.add_link(points[0], points[3])
        network.add_link(points[1], points[4])
        network.add_link(points[2], points[3])
        network.add_link(points[3], points[4])
        network.add_link(points[3], points[6])
        network.add_link(points[4], points[7])
        network.add_link(points[5], points[6])
        network.add_link(points[6], points[7])
        network.add_link(points[6], points[8])
        network.add_link(points[7], points[9])

        table = Table(network)

        self.assertEqual(6, len(table.cells))
