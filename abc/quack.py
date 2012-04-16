"""
Verify duck typing.
"""
__all__ = ["check_class"]
import inspect

def check_class(abstract, concrete):
    """
    Check that a concrete class interface matches the abstract base class.

    Can't check the return types since they are not listed.
    """
    #print "check_class",abstract.__name__,concrete.__name__
    ignore = "__init__", "__doc__"
    items = inspect.getmembers(abstract)
    #items = abstract.__dict__.items()
    for name,abstract_method in items:
        if name in ignore:
            # Can specialize __init__
            continue
        try:
            concrete_method = getattr(concrete, name)
        except AttributeError:
            raise NotImplementedError("%s does not implement %s"
                                      %(concrete.__name__, name))
        #print name,inspect.ismethod(abstract_method), inspect.ismethod(concrete_method)
        if inspect.ismethod(abstract_method) and inspect.ismethod(concrete_method):
            check_method_signature(abstract_method, concrete_method)
        elif type(abstract_method) != type(concrete_method):
            raise NotImplementedError("attribute <%s> differs in class %s"
                                      %(name, concrete.__name__))


def check_method_signature(abstract, concrete):
    """
    Verify that two methods have the same signature.

    Named arguments must be the same, except for self, *args, and **kw.

    Default values should also be the same.

    This won't work with decorators unless they preserve type signature.
    """
    abstract_spec = inspect.getargspec(abstract)
    concrete_spec = inspect.getargspec(concrete)
    #print "args",abstract_spec.args[1:], concrete_spec.args[1:]
    if (abstract_spec.args[1:] != concrete_spec.args[1:]
        or abstract_spec.defaults != concrete_spec.defaults
        or (abstract_spec.varargs is None) != (concrete_spec.varargs is None)
        or (abstract_spec.keywords is None) != (concrete_spec.keywords is None)
        ):
        raise NotImplementedError("%s.%s%s differs from %s.%s%s"
                                  %(concrete.im_class.__name__,
                                    concrete.__name__,
                                    formatargs(concrete_spec),
                                    abstract.im_class.__name__,
                                    abstract.__name__,
                                    formatargs(abstract_spec),
                                    )
                                  )

def formatargs(argspec):
    return inspect.formatargspec(argspec.args,argspec.varargs,
                                 argspec.keywords,argspec.defaults)

def test():
    class A(object):
        color = 'red'
        def a(self, a, b, c=2, *args, **kw): pass
    class Mixin:
        color = 'red'
        def a(self, a, b, c=2, *args, **kw): pass
    class B(object):
        color = 'blue'
        def a(self, a, b, c=2, *varargs, **keywords): pass
    class C(A, object):
        def __init__(self): pass
    class D(Mixin, object):
        def __init__(self): pass
    class B_not_type(object):
        color = 2
        def a(self, a, b, c=2, *varargs, **keywords): pass
    class B_not_def(object):
        color = 'blue'
    class B_missing_attribute(object):
        def a(self, a, b, c=2, *varargs, **keywords): pass
    class B_missing_arg(object):
        color = 'blue'
        def a(self, a, c=2, *varargs, **keywords): pass
    class B_extra_arg(object):
        color = 'blue'
        def a(self, a, c=2, *varargs, **keywords): pass
    class B_missing_varargs(object):
        color = 'blue'
        def a(self, a, c=2, **keywords): pass
    class B_missing_keywords(object):
        color = 'blue'
        def a(self, a, c=2, *varargs): pass

    for cls in B,C,D:
        check_class(A, cls)
        check_class(Mixin, cls)
    for cls in (B_not_type, B_not_def, B_missing_attribute, B_missing_arg,
                B_extra_arg, B_missing_varargs, B_missing_keywords):
        try:
            check_class(A, cls)
            raise Exception("%s did not raise exception"%cls.__name__)
        except NotImplementedError:
            pass
        try:
            check_class(Mixin, cls)
            raise Exception("%s did not raise exception"%cls.__name__)
        except NotImplementedError:
            pass

if __name__ == "__main__":
    test()
