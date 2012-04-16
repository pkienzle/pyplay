Deteremine the fully qualified module name.

Currently one method is presented, which is to use a function defined within the
module and look at fn.__module__.

This implementation uses relative paths, so needs to be tested from the pyplay
root directory using::

    $ PYTHONPATH=. python -m modpath.main

