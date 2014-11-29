from tests.test_basic import TestDocument


class Test130252(TestDocument):
    def test_page_0(self):
        file_name = 'tests/samples/130252.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])


class Test131287(TestDocument):
    def test_page_0(self):
        file_name = 'tests/samples/131287.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])


class Test131288(TestDocument):
    def test_page_0(self):
        file_name = 'tests/samples/131288.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])


class Test131371(TestDocument):
    def test_page_0(self):
        file_name = 'tests/samples/131371.pdf'
        self._run_test(file_name, [0, 1])

        self.assertEqual(self.device.result, [])


class Test131783(TestDocument):
    def test_page_0(self):
        file_name = 'tests/samples/131783.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(self.device.result, [])
