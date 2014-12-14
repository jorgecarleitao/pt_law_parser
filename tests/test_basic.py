import unittest

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from pt_law_parser.converter import LAOrganizer, LawConverter


class TestDocument(unittest.TestCase):

    def get_expected(self, file_name):
        with open(file_name+'.html') as my_file:
            return my_file.read().decode("UTF-8")

    def setUp(self):
        self.rsrcmgr = PDFResourceManager(caching=True)
        params = LAOrganizer()
        self.device = LawConverter(self.rsrcmgr, laparams=params)

    def _run_test(self, file_name, pages):

        fp = file(file_name, 'rb')

        interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)
        for page in PDFPage.get_pages(fp, pagenos=pages):
            interpreter.process_page(page)
        fp.close()

    def _print_result(self, file_name='s.html'):
        """
        Method to print the result of the test to a file, to inspection.
        """
        # to see lines, add <style>table, th, td {border: 1px solid black;
        # border-collapse: collapse;} </style>
        with open(file_name, 'w') as f:
            f.write(self.device.as_html().encode('utf-8'))


class Test01060115(TestDocument):
    """
    This document is pre-2006; it is a different version of DRE.
    """
    def test_page_1(self):
        file_name = 'tests/samples/01060115.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.1').split('\n'))

        self.assertEqual(11, len(self.device.titles))

    def test_page_2(self):
        file_name = 'tests/samples/01060115.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(19, len(self.device.titles))

    def test_page_3(self):
        file_name = 'tests/samples/01060115.pdf'
        self._run_test(file_name, [2])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.3').split('\n'))

        self.assertEqual(12, len(self.device.titles))

    def test_page_6(self):
        file_name = 'tests/samples/01060115.pdf'
        self._run_test(file_name, [5])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.6').split('\n'))

        self.assertEqual(6, len(self.device.titles))

    def test_page_7(self):
        """
        This document is pre-2006; it is a different version of DRE.
        """
        file_name = 'tests/samples/01060115.pdf'
        self._run_test(file_name, [6])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.7').split('\n'))

        self.assertEqual(16, len(self.device.titles))

    def test_page_9(self):
        """
        This document is pre-2006; it is a different version of DRE.
        """
        file_name = 'tests/samples/01060115.pdf'
        self._run_test(file_name, [8])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.9').split('\n'))

        self.assertEqual(13, len(self.device.titles))


class Test0272602741(TestDocument):

    @unittest.expectedFailure
    # this test contains a table where lines in different cells are interpreted as
    # the same line.
    # todo: fix expected failure in test.
    def test_page_1(self):
        file_name = 'tests/samples/0272602741.pdf'

        self._run_test(file_name, [0])

        self.assertEqual(1, len(self.device.tables))
        self.assertEqual(14, len(self.device.titles))

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.1').split('\n'))

    @unittest.expectedFailure
    # there seems to be a shift of the titles on citing bigger than rest of
    # the cited text.
    def test_page_2(self):
        file_name = 'tests/samples/0272602741.pdf'

        self.device._is_citing = True
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(8, len(self.device.titles))

    def test_2_pages(self):
        file_name = 'tests/samples/0272602741.pdf'

        self._run_test(file_name, [6, 7])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.6-7').split('\n'))

        self.assertEqual(1, len(self.device.titles))

    @unittest.expectedFailure
    # see test_page_2.
    def test_page_4(self):
        file_name = 'tests/samples/0272602741.pdf'

        self.device._is_citing = True
        self._run_test(file_name, [4])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.4').split('\n'))

        self.assertEqual(16, len(self.device.titles))


class Test0045800458(TestDocument):

    def test(self):
        file_name = 'tests/samples/0045800458.pdf'
        self._run_test(file_name, None)

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name).split('\n'))

        self.assertEqual(18, len(self.device.titles))


class Test107190(TestDocument):

    def test_page_2(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(14, len(self.device.titles))

    def test_page_5(self):
        """
        Page with a complex column organization.
        """
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [4])

        self.assertEqual(3, len(self.device.tables))
        self.assertEqual(5, len(self.device.titles))

    def test_page_7(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [6])

        self.assertEqual(1, len(self.device.tables))
        self.assertEqual(4, len(self.device.result))

    def test_page_12(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [11])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.12').split('\n'))

        self.assertEqual(6, len(self.device.titles))


class Test108839(TestDocument):

    def test_page_2(self):
        """
        Page with a complex column organization.
        """
        file_name = 'tests/samples/108839.pdf'

        self.device._is_citing = True
        self._run_test(file_name, [1])

        self.assertEqual(4, len(self.device.titles))

    def test_page_9(self):
        """
        Page with a complex column organization.
        """
        file_name = 'tests/samples/108839.pdf'

        self.device._is_citing = True
        self._run_test(file_name, [8])

        self.assertEqual(21, len(self.device.titles))


class Test113604(TestDocument):
    @unittest.expectedFailure
    # It identifies extra paragraphs corresponding to two sub-lines.
    # todo: distinguish them.
    def test_page_3(self):
        file_name = 'tests/samples/113604.pdf'
        self._run_test(file_name, [2])

        self.assertEqual(15, len(self.device.titles))
        self.assertEqual(36, len(self.device.paragraphs))


class Test116008(TestDocument):
    @unittest.expectedFailure
    # Same as Test113604.test_page_3
    def test_page_2(self):
        file_name = 'tests/samples/116008.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(11, len(self.device.titles))

    def test_page_4(self):
        file_name = 'tests/samples/116008.pdf'
        self._run_test(file_name, [3])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.4').split('\n'))

        self.assertEqual(12, len(self.device.titles))
        self.assertEqual(3, len(self.device.tables))

    @unittest.expectedFailure
    # this page contains a page with two centered columns.
    # todo: generalize the algorithm for 2 centered columns.
    def test_page_6(self):
        file_name = 'tests/samples/116008.pdf'
        self._run_test(file_name, [5])

        self.assertEqual(22, len(self.device.titles))
        self.assertEqual(2, len(self.device.tables))

    def test_page_8(self):
        file_name = 'tests/samples/116008.pdf'
        self._run_test(file_name, [7])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.8').split('\n'))

        self.assertEqual(17, len(self.device.titles))

    def test_page_9(self):
        file_name = 'tests/samples/116008.pdf'
        self._run_test(file_name, [8])

        self.assertEqual(8, len(self.device.titles))


class Test118381(TestDocument):
    def test_page_2(self):
        """
        A case where there is a paragraph with a different paragraph space
        """
        file_name = 'tests/samples/118381.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

    def test_page_4(self):
        """
        A case where there is a paragraph with a different paragraph space
        """
        file_name = 'tests/samples/118381.pdf'
        self._run_test(file_name, [3])

        self.assertEqual(8, len(self.device.titles))

    def test_page_5(self):
        """
        A case where there is a paragraph with a different paragraph space
        """
        file_name = 'tests/samples/118381.pdf'
        self._run_test(file_name, [4])

        self.assertEqual(2, len(self.device.titles))

    def test_page_6(self):
        """
        A case where there is a paragraph with a different paragraph space
        """
        file_name = 'tests/samples/118381.pdf'
        self._run_test(file_name, [5])

        self.assertEqual(13, len(self.device.titles))


class Test128839(TestDocument):
    def test_page_1(self):
        file_name = 'tests/samples/128839.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(13, len(self.device.titles))


class Test130252(TestDocument):
    def test_page_2(self):
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(15, len(self.device.titles))

    def test_page_3(self):
        """
        Big tables and centered titles
        """
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [2])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.3').split('\n'))

        self.assertEqual(6, len(self.device.titles))

    def test_page_4(self):
        """
        Big tables, centered titles and image.
        """
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [3])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.4').split('\n'))

        self.assertEqual(4, len(self.device.titles))

    def test_page_8(self):
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [7])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.8').split('\n'))

        self.assertEqual(14, len(self.device.titles))


class Test131287(TestDocument):
    def test_page_2(self):
        file_name = 'tests/samples/131287.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(15, len(self.device.titles))


class Test131783(TestDocument):
    def test_page_2(self):
        file_name = 'tests/samples/131783.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(6, len(self.device.titles))


class Test131288(TestDocument):

    def test_page_6(self):
        """
        Contains a line starting with a start citing char, showing that
        start citing must be done taking that into account.
        """
        file_name = 'tests/samples/131288.pdf'
        self._run_test(file_name, [5])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.6').split('\n'))

        self.assertEqual(18, len(self.device.titles))


class Test131371(TestDocument):

    @unittest.expectedFailure
    # This test fails because the table contains a list of numbers on the same
    # cell but in different paragraphs. The list is centered, and is difficult to
    # distinguish from a normal paragraph.
    # todo: fix this by improving how the table interprets a new line.
    def test_page_4(self):
        """
        Contains a table on the right column.

        Also, the table contains centered paragraphs difficult to identify.
        """
        file_name = 'tests/samples/131371.pdf'
        self._run_test(file_name, [3])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.4').split('\n'))


class Test135502(TestDocument):

    @unittest.expectedFailure
    # todo: there is a form here. Maybe we can track it via a rectangle.
    def test_page_5(self):
        file_name = 'tests/samples/135502.pdf'
        self._run_test(file_name, [4])

        self._print_result()

        self.assertEqual(10, len(self.device.titles))

    @unittest.expectedFailure
    # see test_page_5
    def test_page_6(self):
        file_name = 'tests/samples/135502.pdf'
        self._run_test(file_name, [5])

        self._print_result()

        self.assertEqual(7, len(self.device.titles))

    def test_page_8(self):
        """
        Page with 3 features:
        * there is a table in the end of the left column.
        * some titles are centered in the PDF in an unusual manner.
        * one table does not contain the bottom border.
        """
        file_name = 'tests/samples/135502.pdf'
        self._run_test(file_name, [7])

        self.assertEqual(19, len(self.device.titles))

        self.assertEqual(8, len(self.device.tables[0].cells))
        self.assertEqual(6, len(self.device.tables[1].cells))
        self.assertEqual(6, len(self.device.tables[2].cells))

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.8').split('\n'))

    def test_page_13(self):
        """
        Page with two images and no text.
        """
        file_name = 'tests/samples/135502.pdf'
        self._run_test(file_name, [12])

        self.assertEqual(0, len(self.device.titles))
