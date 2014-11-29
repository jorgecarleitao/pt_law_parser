from tests.test_basic import TestDocument


class TestDocStart(TestDocument):

    def test_130252(self):
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])

    def test_131287(self):
        file_name = 'tests/samples/131287.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])

    def test_131288(self):
        file_name = 'tests/samples/131288.pdf'
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


class TestDocEnd(TestDocument):
    """
    Tests that we correctly ignore the content of the last page related with
    price of the document and address.
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
