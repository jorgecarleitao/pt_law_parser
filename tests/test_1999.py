from test_basic import TestDocument


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
