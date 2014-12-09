from pt_law_parser.parser import parse_document

from tests.test_basic import TestDocument


class TestParser(TestDocument):
    """
    This test case shows that documents from different years are parsed without
    errors.
    """
    def test_107190(self):
        """
        Document from 1997.
        """
        device = parse_document('tests/samples/107190.pdf')

        self.assertEqual(13, len(device.meta.pages))

    def test_108839(self):
        """
        Document from 1998.
        """
        device = parse_document('tests/samples/108839.pdf')

        self.assertEqual(27, len(device.meta.pages))

    def test_113604(self):
        """
        Document from 2000.
        """
        device = parse_document('tests/samples/113604.pdf')

        self.assertEqual(4, len(device.meta.pages))

    def test_116008(self):
        """
        Document from 2001.
        """
        device = parse_document('tests/samples/116008.pdf')

        self.assertEqual(9, len(device.meta.pages))

    def test_130252(self):
        """
        Document from 2010.
        """
        device = parse_document('tests/samples/130252.pdf')

        self.assertEqual(18, len(device.meta.pages))

    def test_131288(self):
        """
        Document from 2010 with two summary pages.
        """
        device = parse_document('tests/samples/131288.pdf')

        self.assertEqual(9, len(device.meta.pages))

    def test_131371(self):
        """
        Document from 2010 with content in last page.
        """
        device = parse_document('tests/samples/131371.pdf')

        self.assertEqual(4, len(device.meta.pages))
