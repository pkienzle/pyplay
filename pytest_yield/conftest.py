"""
pytest hooks for yield tests
----------------------------

Rather than using `pytest.mark.parametrize`, create a set of tests using
a generator which yields test function and args.  This allows for lazy
generation of test cases, which only appear when pytest is run rather than
module load time.

For example::

    def isequal(a, b):
        assert a == b

    def test_equal():
        for a, b in ((1, 1), (1, 2), (2, 2)):
            yield isequal, a, b

Can explicitly name the test cases by giving a description before the function:

    def test_equal_named():
        for a, b, in ((1, 1), (1, 2), (2, 2)):
            yield "%d-%d"%(a, b), isequal, a, b

Can also yield individual unittest test cases or entire test suites.
"""
from __future__ import print_function

import sys
import copy
import inspect
import unittest

import pytest
from _pytest.unittest import TestCaseFunction

def pytest_pycollect_makeitem(collector, name, obj):
    """
    Convert test generator into list of function tests so that pytest doesn't
    complain about deprecated yield tests.
    """
    if inspect.isgeneratorfunction(obj):
        tests = []
        for number, yielded in enumerate(obj()):
            if isinstance(yielded, unittest.TestSuite):
                tests.extend(_yield_unittest_case(collector, name, item)
                             for item in yielded)
            elif isinstance(yielded, unittest.TestCase):
                tests.append(_yield_unittest_case(collector, name, yielded))
            else:
                index, call, args = _split_yielded_test(yielded, number)
                test = pytest.Function(name+index, collector, args=args, callobj=call)
                tests.append(test)
        return tests

def _yield_unittest_case(collector, name, obj):
    method = obj._testMethodName
    setup = getattr(obj, 'setUp', lambda: None)
    call = getattr(obj, method)
    teardown = getattr(obj, 'tearDown', lambda: None)
    def run():
        setup()
        try:
            call()
        finally:
            teardown()
    # TODO: description is available as obj.shortDescription()
    args = ()
    index = "[%s]" % method
    test = pytest.Function(name+index, collector, args=args, callobj=run)
    return test

def _split_yielded_test(obj, number):
    if not isinstance(obj, (tuple, list)):
        # Turn bare function into tuple of function and no args.
        obj = (obj,)
    if not callable(obj[0]):
        # Allow (index, function, args), with index as string.
        index = "[%s]"%(str(obj[0]),)
        obj = obj[1:]
    else:
        # Otherwise index is the sequence number.
        index = "[%d]"%number
    call, args = obj[0], obj[1:]
    return index, call, args

USE_DOCSTRING_AS_DESCRIPTION = True
def pytest_collection_modifyitems(session, config, items):
    """
    Add description to the test node id if item is a function and function
    has a description attribute or __doc__ attribute.
    """
    for item in items:
        if isinstance(item, pytest.Function):
            if isinstance(item, TestCaseFunction):
                # TestCase uses item.name to find the method so skip
                continue
            function = item.obj

            # If the test case provides a "description" attribute then use it
            # as an extended description.  If there is no description attribute,
            # then perhaps use the test docstring.
            if USE_DOCSTRING_AS_DESCRIPTION:
                description = getattr(function, 'description', function.__doc__)
            else:
                description = getattr(function, 'description', "")

            # If description is not supplied but yield args are, then use the
            # yield args for the description
            if not description and getattr(item, '_args', ()):
                description = (str(item._args[0]) if len(item._args) == 1
                               else str(item._args))

            # Set the description as part of the node identifier.
            if description:
                # Strip spaces from start and end and strip dots from end
                # pytest converts '.' to '::' on output for some reason.
                description = description.strip().rstrip('.')
                # Join multi-line descriptions into a single line
                if '\n' in description:
                    description = " ".join(line.strip()
                                           for line in description.split('\n'))

                # Note: leave the current name mostly as-is since the prefix
                # is needed to specify the nth test from a list of tests.
                item.name += "::" + description
                item._nodeid += "::" + description
                #print("-"*20)
                #for attr in dir(item):
                #    if attr not in ('Class','File','Function','Instance',
                #            'Item','Module'):
                #        print(attr, getattr(item, attr))
