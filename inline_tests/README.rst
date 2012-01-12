Question
========

Does nosetest allow me to use tests in code with relative imports?

Answer
======

Yes!  No need for separate test directory for simple tests when using
relative imports.

Furthermore, if the test is in a __name__ == "__main__" block, you can
run it directly using::

    $ python -m package.module

Test
====

run the following from the directory above::

    PYTHONPATH=. nosetests inline_tests/core.py
