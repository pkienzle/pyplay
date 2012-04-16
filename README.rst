PyPlay is a set of small tests, mostly of features of python, but it also includes
some math experiments.

Math
====

`empirical_ci <pyplay/tree/master/empirical_ci>`_

    determine how many samples we need to compute 1-sigma

Python
======

`inline_tests <pyplay/tree/master/inline_tests>`_

    does nosetest allow relative imports?

`limits <pyplay/tree/master/limits>`_

    how do I use resource limits on python processes?

`mapapply <pyplay/tree/master/mapapply>`_

    How do I use multiprocess map with functions that take multiple arguments

`abc <pyplay/tree/master/abc>`_

    Explore abstract base class support, checking that missing subclass methods
    get reported and method signatures on the subclass match the base class.  It
    turns out that abc's do not check method signatures, so pyplay/abc contains
    the module `quack <pyplay/tree/master/abc/quack.py>`_ which does the work of 
    abc as well as checking method signatures.

`module_attr <pyplay/tree/master/module_attr>`_

    Show that globals are defined by first assignment to the global, not by a
    module level global statement.  

`modpath <pyplay/tree/master/modpath>`_

    Explore ways to find the module path.  Currently this uses fn.__module__ where
    fn is a function defined within the module.  This meets my immediate needs,
    so I didn't explore any other solutions.

WxPython
========

`aui <pyplay/tree/master/aui>`_

    test of floating notebooks

`mplinteractor <pyplay/tree/master/aui>`_

    interactors on matplotlib graphs

