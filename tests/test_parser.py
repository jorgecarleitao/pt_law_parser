import unittest

from pt_law_parser.parser import parse_document

from tests.test_basic import TestDocument


class TestParser(TestDocument):
    """
    This test case shows that documents from different years are parsed without
    errors.
    """
    @unittest.expectedFailure
    # See expected failure test_basic.Test107190.test_page_12.
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

    @unittest.expectedFailure
    # See expected failure test_basic.Test116008.test_page_4.
    def test_116008(self):
        """
        Document from 2001.
        """
        device = parse_document('tests/samples/116008.pdf')

        self.assertEqual(9, len(device.meta.pages))

    def test_118381(self):
        """
        Document from 2002.
        """
        device = parse_document('tests/samples/118381.pdf')

        self.assertEqual(5, len(device.meta.pages))

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

    def test_131869(self):
        """
        Document from 2011.
        """
        device = parse_document('tests/samples/131869.pdf')

        self.assertEqual(5, len(device.meta.pages))

    def test_133880(self):
        """
        Document from 2012.
        """
        device = parse_document('tests/samples/133880.pdf')

        self.assertEqual(14, len(device.meta.pages))

    def test_135502(self):
        """
        Document from 2013.
        """
        device = parse_document('tests/samples/135502.pdf')

        self.assertEqual(26, len(device.meta.pages))
