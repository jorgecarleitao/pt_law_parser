import unittest

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from pt_law_parser.converter import LAOrganizer, LawConverter


class TestDocument(unittest.TestCase):

    def get_expected(self, file_name):
        with open(file_name+'.html') as my_file:
            return my_file.read().decode("UTF-8")

    def _run_test(self, file_name, pages):
        rsrcmgr = PDFResourceManager(caching=True)

        fp = file(file_name, 'rb')

        params = LAOrganizer()

        self.device = LawConverter(rsrcmgr, laparams=params)

        interpreter = PDFPageInterpreter(rsrcmgr, self.device)
        for page in PDFPage.get_pages(fp, pagenos=pages):
            interpreter.process_page(page)
        fp.close()


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

    def test_page_2(self):
        file_name = 'tests/samples/0272602741.pdf'

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

    def test_page_4(self):
        file_name = 'tests/samples/0272602741.pdf'

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
        Big tables and centered titles
        """
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [3])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.4').split('\n'))

        self.assertEqual(4, len(self.device.titles))

    def test_page_8(self):
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [7])

        with open('s.html', 'w') as f:
            f.write(self.device.as_html().encode('utf-8'))

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
