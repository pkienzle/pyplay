from __future__ import print_function
import unittest

def isequal(a, b):
    assert a == b

def isnotequal(a, b):
    assert a != b

def test_equal():
    for k in range(3):
        #yield isequal, k, k+1
        yield isequal, k, k

#@unittest.expectedFailure
#def test_equal_fail():
#    for k in range(3):
#        yield isequal, k, k+1

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

@unittest.skip("we can use builtin unittest.skip")
def test_both():
    for k in range(3):
        for test in (isequal, isnotequal):
            yield test.__name__, test, k, k

def build_suite():
    class WidgetTest(unittest.TestCase):
        def setUp(self):
            self.widget = (30, 30)
        @unittest.skip("testing skip")
        def test_default_widget_size(self):
            self.assertEqual(self.widget, (30, 30))
        @unittest.expectedFailure
        def test_fail(self):
            self.assertEqual(1, 0, "broken")
        @unittest.skip("comment out skip to show failure on success")
        @unittest.expectedFailure
        def test_dont_fail(self):
            self.assertEqual(1, 1, "broken")
        def test_widget_resize(self):
            self.widget = (100, 150)
            self.assertEqual(self.widget, (100, 150))
    class MyTestCase(unittest.TestCase):
        def test_add(self):
            self.assertEqual(1+1, 2)
    def addtests(suite, case):
        for method in dir(case):
            if method.startswith('test_'):
                suite.addTest(case(method))
    suite = unittest.TestSuite()
    addtests(suite, WidgetTest)
    addtests(suite, MyTestCase)
    return suite

def test_suite():
    yield build_suite()

def test_cases():
    for test in build_suite():
        yield test
