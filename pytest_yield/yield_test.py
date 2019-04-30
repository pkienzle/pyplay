from __future__ import print_function

def isequal(a, b):
    assert a == b

def isnotequal(a, b):
    assert a != b

def test_equal():
    for k in range(3):
        #yield isequal, k, k+1
        yield isequal, k, k

def test_equal_desc():
    for k in ('a', 'b', 'c'):
        #f = lambda: isequal(k, k+'x')
        f = lambda: isequal(k, k)
        f.description = k
        yield f

def test_equal_desc2():
    for k in ('a', 'b', 'c'):
        #yield "testing "+k, isequal, k, k+'x'
        yield "test_"+k, isequal, k, k

def test_both():
    for k in range(3):
        #yield isequal, k, k+1
        for test in (isequal, isnotequal):
            yield test.__name__, test, k, k

def build_suite():
    import unittest
    class WidgetTest(unittest.TestCase):
        def setUp(self):
            self.widget = (30, 30)
        @unittest.skip("testing skip")
        def test_default_widget_size(self):
            self.assertEqual(self.widget, (30, 30))
        def test_widget_resize(self):
            self.widget = (100, 150)
            self.assertEqual(self.widget, (100, 150))
    class MyTestCase(unittest.TestCase):
        def test_add(self):
            self.assertEqual(1+1, 2)
    suite = unittest.TestSuite()
    suite.addTest(WidgetTest('test_default_widget_size'))
    suite.addTest(WidgetTest('test_widget_resize'))
    suite.addTest(MyTestCase('test_add'))
    return suite

def test_suite():
    yield build_suite()

def test_cases():
    for test in build_suite():
        yield test
