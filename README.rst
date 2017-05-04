PyPlay is a set of small tests, mostly of features of python, but it also includes
some math experiments.

Note: use `rest2html <https://raw.github.com/github/markup/master/lib/github/commands/rest2html>`_ to check README.rst before checkin

Math
====

`<empirical_ci>`_

    determine how many samples we need to compute 1-sigma

`<poisson_peak>`_

    peak fitting with gaussian vs. poisson statistics

`<BIC>`_

    test distribution of chisq values for nested models with BIC

`<count_by_roi>`_

    counting until time vs counting until count gives different rate estimates

Python
======

`<excutil.py>`_

    annotate a python exception, for example, by adding details of
    what operation was being performed when the exception occurred

`<inline_tests>`_

    does nosetest allow relative imports?

`<limits>`_

    how do I use resource limits on python processes?

`<mapapply>`_

    How do I use multiprocess map with functions that take multiple arguments

`<abc>`_

    Explore abstract base class support, checking that missing subclass methods
    get reported and method signatures on the subclass match the base class.  It
    turns out that abc's do not check method signatures, so pyplay/abc contains
    the module `quack <abc/quack.py>`_ which does the work of
    abc as well as checking method signatures.

`<module_attr>`_

    Show that globals are defined by first assignment to the global, not by a
    module level global statement.

`<modpath>`_

    Explore ways to find the module path.  Currently this uses fn.__module__ where
    fn is a function defined within the module.  This meets my immediate needs,
    so I didn't explore any other solutions.

`<byline.py>`_

    Implement line buffering on streams that don't have it.  Turns out I don't
    need this code because the problem I was trying to solve (BZ2 files cutting
    off early because they used a flush each line) is already solved in python
    3.2.

WxPython
========

`<aui>`_

    test of floating notebooks

`<mplinteractor>`_

    interactors on matplotlib graphs

Web
===

`<ajax>`_

    play with simple web applications and python cgi

`<webkit.py>`_

    Use PyQt4 with webkit as an app ui.  Demonstrates calling python from
    javascript and javascript from python.
