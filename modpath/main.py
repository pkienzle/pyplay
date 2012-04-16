import sys,os
from .subpackage import submod

def main():
    print "From main, use path.to.module.fn.__module__",submod.fn.__module__
    submod.fn()
    print "package directory for submod",os.path.dirname(sys.modules[submod.__name__].__file__)
    print "full path package directory for submod",os.path.abspath(os.path.dirname(sys.modules[submod.__name__].__file__))

if __name__ == "__main__":
    main()
