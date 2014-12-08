from pt_law_parser.parser import parse_document

from tests.test_basic import TestDocument


class TestParser(TestDocument):

    def test_130252_pages_number(self):
        device = parse_document('tests/samples/130252.pdf')

        self.assertEqual(18, len(device.meta.pages))

    def test_113604_pages_number(self):
        device = parse_document('tests/samples/113604.pdf')

        self.assertEqual(4, len(device.meta.pages))

    def test_131288(self):

        device = parse_document('tests/samples/131288.pdf')

        self.assertEqual(9, len(device.meta.pages))

    def test_131371(self):

        device = parse_document('tests/samples/131371.pdf')

        self.assertEqual(4, len(device.meta.pages))

    def test_107190(self):
        """
        Document from 1997.
        """
        device = parse_document('tests/samples/107190.pdf')

        self.assertEqual(13, len(device.meta.pages))
