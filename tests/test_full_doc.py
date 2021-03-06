from tests.test_basic import TestDocument


class TestDocStart(TestDocument):
    """
    Test case intended to show that summary pages of a document are correctly
    ignored.
    """
    def test_107190_page_1(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))

    def test_113604_page_1(self):
        file_name = 'tests/samples/113604.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))

    def test_113604_page_2(self):
        file_name = 'tests/samples/113604.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))

    def test_130252(self):
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])

    def test_131287(self):
        file_name = 'tests/samples/131287.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])

    def test_131371(self):
        file_name = 'tests/samples/131371.pdf'
        self._run_test(file_name, [0, 1])

        self.assertEqual(self.device.result, [])

    def test_131783(self):
        file_name = 'tests/samples/131783.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])

    def test_131869(self):
        file_name = 'tests/samples/131869.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])

    def test_137070(self):
        """
        Document from 2014.
        """
        file_name = 'tests/samples/137070.pdf'
        self._run_test(file_name, [0, 1, 2, 3])

        self.assertEqual(self.device.result, [])


class TestDocEnd(TestDocument):
    """
    Tests that we correctly ignore the content of the last pages.
    """
    def test_130252(self):
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [18, 19])

        self.assertEqual(u'<p>O presente',
                         self.device.result[-1].as_html()[:13])

    def test_131783(self):
        file_name = 'tests/samples/131783.pdf'
        self._run_test(file_name, [3])

        # the contains only 4 paragraphs.
        self.assertEqual(4, len(self.device.result))

    def test_133880(self):
        file_name = 'tests/samples/133880.pdf'
        self._run_test(file_name, [15])

        self.assertEqual(0, len(self.device.titles))
        self.assertTrue(self.device.result[-1].as_html().startswith('<table>'))

    def test_107190_empty_page(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [14])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))

    def test_107190(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [15])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))

    def test_137056(self):
        file_name = 'tests/samples/137056.pdf'
        self._run_test(file_name, [5])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))
