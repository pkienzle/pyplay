Question
========

Does nosetest allow me to use tests in code with relative imports?

Lately, I've been moving tests to a separate test directory because
relative imports do not work when run as __main__.

Test
====

run the following from the directory above::

    PYTHONPATH=. nosetests inline_tests/core.py

Answer
======

Yes!  No need for separate test directory for simple tests when using
relative imports.

Furthermore, if the test is in a __name__ == "__main__" block, you can
run it directly using::

    $ python -m package.module
