from test_basic import TestDocument


class Test107190(TestDocument):
    def test_page_1(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))

    def test_page_15(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [14])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))

    def test_page_16(self):
        file_name = 'tests/samples/107190.pdf'
        self._run_test(file_name, [15])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))
