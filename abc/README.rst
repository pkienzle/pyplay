ABC
===

Example of using the python abstract base classes with or without missing
package overrides.

To show that the correctly instantiated concrete class works use::

    $ python sub.py

To show that a missing function implementation fails, use::

    $ python submissing.py

Python's abc does not check argument signature on the implementation!  The following
should fail, but doesn't::

    $ python badargs.py

The module :file:`quack.py` checks whether the concrete class walks like a duck, as
is shown here::

    $ python checkargs.py

Note that quack.py can be used as a complete replacement for the abc, in that it will
check that all required classes from the base class are implemented without having to
subclass from the base class.  The check is done once at load time, so it has a similar
cost.

