from pt_law_parser.parser import parse_document

from tests.test_basic import TestDocument


class TestParser(TestDocument):

    def test_130252_pages_number(self):
        device = parse_document('tests/samples/130252.pdf')

        self.assertEqual(19, len(device.meta.pages))

    def test_113604_pages_number(self):
        device = parse_document('tests/samples/113604.pdf')

        self.assertEqual(4, len(device.meta.pages))
