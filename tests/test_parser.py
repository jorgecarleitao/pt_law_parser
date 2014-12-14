import unittest

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

        self.assertEqual(14 + 13 + 4 + 5 + 0 + 0 + 2 + 0 + 5 + 21 + 6 + 18 + 8,
                         len(device.titles))

    def test_108839(self):
        """
        Document from 1998.
        """
        device = parse_document('tests/samples/108839.pdf')

        self.assertEqual(27, len(device.meta.pages))

        self.assertEqual(4 + 14 + 12 + 12 + 16 + 18 + 16 + 21 + 16 + 16 + 20 +
                         16 + 16 + 20 + 12 + 12 + 18 + 18 + 22 + 24 + 6 + 24 +
                         20 + 16 + 23 + 26 + 22,
                         len(device.titles))

    def test_113604(self):
        """
        Document from 2000.
        """
        device = parse_document('tests/samples/113604.pdf')

        self.assertEqual(4, len(device.meta.pages))

        self.assertEqual(15 + 2 + 3, len(device.titles))

    @unittest.expectedFailure
    # See expected failure of test_basic.Test116008.test_page_6.
    def test_116008(self):
        """
        Document from 2001.
        """
        device = parse_document('tests/samples/116008.pdf')

        self.assertEqual(9, len(device.meta.pages))

        self.assertEqual(11 + 13 + 12 + 18 + 22 + 6 + 17 + 8 + 8,
                         len(device.titles))

    def test_118381(self):
        """
        Document from 2002.
        """
        device = parse_document('tests/samples/118381.pdf')

        self.assertEqual(5, len(device.meta.pages))

        self.assertEqual(18 + 16 + 8 + 2 + 13, len(device.titles))

    def test_130252(self):
        """
        Document from 2010.
        """
        device = parse_document('tests/samples/130252.pdf')

        self.assertEqual(18, len(device.meta.pages))

        self.assertEqual(15 + 6 + 4 + 21 + 21 + 13 + 14 + 24 + 8 + 20 + 10 + 16 +
                         14 + 12 + 16 + 14 + 14 + 18, len(device.titles))

    def test_131869(self):
        """
        Document from 2011.
        """
        device = parse_document('tests/samples/131869.pdf')

        self.assertEqual(5, len(device.meta.pages))

        self.assertEqual(14 + 4 + 4 + 6, len(device.titles))

    def test_133880(self):
        """
        Document from 2012.
        """
        device = parse_document('tests/samples/133880.pdf')

        self.assertEqual(14, len(device.meta.pages))

        self.assertEqual(14 + 14 + 8 + 14 + 11 + 12 + 10 + 14 + 13 + 3,
                         len(device.titles))

    @unittest.expectedFailure
    def test_135502(self):
        """
        Document from 2013.
        """
        device = parse_document('tests/samples/135502.pdf')

        self.assertEqual(25, len(device.meta.pages))

        expected = 14 + 14 + 10 + 7 + 19 + 17 + 1 + 4 + 7 + 10 + 17 + 14 + 16 +\
            22 + 14 + 12 + 23 + 18 + 14 + 25 + 14 + 16 + 26
        # See test_basic.Test135502 for why this fails.
        self.assertEqual(expected, len(device.titles))

    def test_137056(self):
        """
        Document from 2014.
        """
        device = parse_document('tests/samples/137056.pdf')

        self.assertEqual(4, len(device.meta.pages))

        self.assertEqual(13, len(device.titles))
        self.assertEqual(1, len(device.tables))
