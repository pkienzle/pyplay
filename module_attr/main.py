#!/usr/bin/env python
import module

print "before set_global",hasattr(module,'some_global')
module.set_global()
print "after set_global",hasattr(module,'some_global')
