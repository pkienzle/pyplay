"""
Verify duck typing.
"""
__all__ = ["implements"]
import inspect

import abc

def implements(interface, implementation=None):
    """
    Check that a implementation class interface matches the interface class.

    Can't check the return types since they are not listed.

    If the implementation class is not specified, return a decorator that
    accepts a implementation class.

    If the interface class is an ABC, only the abstract methods are
    checked, otherwise all names which do not start with an underscore
    are checked.  Interface attributes should be types.

    Note: we could allow underscore names to be checked as well, for example
    by seeing if the underscore name has the same value as its parent
    underscore name.  For now, just define your interface class as an ABC,
    or explicitly list the names of all the classes you want to check in
    __abstractmethods__. [Caveat: haven't tried]
    """
    if implementation is None:
        return lambda cls: implements(interface, cls)

    #print "implements",interface.__name__,implementation.__name__
    items = inspect.getmembers(interface)
    abstract_methods = getattr(interface, "__abstractmethods__",None)
    #items = interface.__dict__.items()
    for name,value in items:
        #print name,inspect.ismethod(abstract_method), inspect.ismethod(concrete_method)
        if inspect.ismethod(value):
            # If interface is an ABC then only use names that are tagged as abstract
            if (abstract_methods and name not in abstract_methods) or name.startswith('_'):
                continue
            concrete_method = getattr(implementation, name, None)
            # If interface is an ABC then make sure the implementation overrides
            # the method, otherwise just check that the method is present
            if (abstract_methods and concrete_method == value) or not inspect.ismethod(concrete_method):
                raise NotImplementedError("%s does not implement %s"
                                          %(implementation.__name__, name))
            # check that the implementation interface is correct
            check_method_signature(value, concrete_method)
        else:
            if name.startswith('_'):
                continue
            # ABCs don't mark required attributes, nor do they need to since
            # these will be inherited from the ABC.  Duck types needs to
            # explicitly check for the required attributes.  We do check that
            # the attribute types match for both ABCs and regular classes.
            try:
                concrete_value = getattr(implementation, name)
            except AttributeError:
                raise NotImplementedError("%s does not define %s"
                                          %(implementation.__name__, name))

            interface_type = value if inspect.isclass(value) else type(value) if value is not None else object
            if not isinstance(concrete_value, interface_type):
                raise NotImplementedError("attribute <%s> type differs in class %s"
                                          %(name, implementation.__name__))

    # If called from a decorator, need to return the implementation class
    return implementation

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
    class ABC(object):
        __metaclass__ = abc.ABCMeta
        color = 'red'
        @abc.abstractmethod
        def a(self, a, b, c=2, *args, **kw): pass
        def b(self): pass
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
    class E(ABC):
        def a(self, a, b, c=2, *varargs, **kw): pass
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
    class E_bad_sig(ABC):
        def a(self): pass
    class E_missing(ABC):
        pass

    for cls in B,C,D,E:
        implements(A, cls)
        implements(ABC, cls)
        implements(Mixin, cls)
    for cls in (B_not_type, B_not_def, B_missing_attribute, B_missing_arg,
                B_extra_arg, B_missing_varargs, B_missing_keywords):
        try:
            implements(A, cls)
            raise Exception("%s did not raise exception"%cls.__name__)
        except NotImplementedError:
            pass
        try:
            implements(ABC, cls)
            raise Exception("%s did not raise exception"%cls.__name__)
        except NotImplementedError:
            pass
        try:
            implements(Mixin, cls)
            raise Exception("%s did not raise exception"%cls.__name__)
        except NotImplementedError:
            pass
    for cls in (E_bad_sig, E_missing):
        try:
            implements(ABC, cls)
            raise Exception("%s did not raise exception"%cls.__name__)
        except NotImplementedError:
            pass

if __name__ == "__main__":
    test()
