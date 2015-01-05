import unittest

from pt_law_parser.network import UndirectedNetwork
from pt_law_parser.point import Point


class TestCase(unittest.TestCase):

    def test_a(self):
        network = UndirectedNetwork()

        points = {Point((0, 0)), Point((1, 0)), Point((0, 1)), Point((1, 1))}
        for point in points:
            network.add_point(point)

        network.add_link(Point((0, 0)), Point((0, 1)))
        network.add_link(Point((0, 0)), Point((1, 0)))
        network.add_link(Point((0, 1)), Point((1, 1)))
        network.add_link(Point((1, 0)), Point((1, 1)))

        self.assertEqual(4, len(network))
        self.assertEqual(4, len(network.links_list()))

        network.remove_point(Point((0, 0)))

        self.assertEqual(3, len(network))
        self.assertEqual(2, len(network.links_list()))

        network.remove_link(Point((0, 1)), Point((1, 1)))
        self.assertEqual(1, len(network.links_list()))
