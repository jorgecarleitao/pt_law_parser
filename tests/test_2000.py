from test_basic import TestDocument


class Test113604(TestDocument):
    def test_page_1(self):
        file_name = 'tests/samples/113604.pdf'
        self._run_test(file_name, [0])

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))

    def test_page_2(self):
        file_name = 'tests/samples/113604.pdf'
        self._run_test(file_name, [1])

        with open('s.html', 'w') as f:
            f.write(self.device.as_html().encode('utf-8'))

        self.assertEqual(0, len(self.device.titles))
        self.assertEqual(0, len(self.device.result))
