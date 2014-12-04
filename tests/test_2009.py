from test_basic import TestDocument


class Test128839(TestDocument):
    def test_page_1(self):
        file_name = 'tests/samples/128839.pdf'
        self._run_test(file_name, [1])

        self.assertEqual(self.device.as_html().split('\n'),
                         self.get_expected(file_name+'.2').split('\n'))

        self.assertEqual(13, len(self.device.titles))
