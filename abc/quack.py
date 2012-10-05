"""
Verify duck typing.
"""
__all__ = ["implements"]
import inspect

import abc
from abc import abstractmethod, abstractproperty

def implements(interface, implementation=None):
    """
    Check that a implementation class interface matches the interface class.

    Methods in the implementation class should have the same parameters 
    in the same order as those in the interface class.  Method return 
    types are not specified, and can't be checked in advance.

    Attributes in the interface should be present in the implementation.
    If the interface attribute is a type or a value, then the implementation
    attribute value should have the same type.  If the interface attribute
    is None, then only the presence test is performed.

    Implementation can be checked at load time using the decorator syntax:

        @implements(Base)
        class Subclass(object):
            ...

    or at run time using the function call syntax:

        try:
            implements(Base, Subclass)
        except NotImplementedError, exc:
            print exc

    By default only the public names are checked.  If you need to check 
    names which start with underscore either list all checked methods
    in the __abstractmethods__ class attribute, or use the usual python
    abc module to define the abstract methods.  The abc module does not
    check attribute types or method signatures, so you will still want 
    to use the implements function to check abcs.
    """
    if implementation is None:
        return lambda cls: implements(interface, cls)

    #print "implements",interface.__name__,implementation.__name__
    items = inspect.getmembers(interface)
    abstract_methods = getattr(interface, "__abstractmethods__",None)
    #print "abstract methods",abstract_methods
    #import pprint; pprint.pprint(items)
    #items = interface.__dict__.items()
    for name,value in items:
        #print name,inspect.ismethod(value)#, inspect.ismethod(concrete_method)
        if inspect.ismethod(value):
            # If interface is an ABC then only use names that are tagged 
            # as abstract; if interface is not an ABC then only use the
            # public names (i.e., those which don't start with '_')
            if ((abstract_methods and name not in abstract_methods) 
                or name.startswith('_')):
                continue
            concrete_method = getattr(implementation, name, None)
            # If interface is an ABC then make sure the implementation overrides
            # the method, otherwise just check that the method is present
            if (not inspect.ismethod(concrete_method) 
                or getattr(concrete_method, '__isabstractmethod__',False)):
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

            interface_type = (value if inspect.isclass(value) else
                              type(value) if value is not None else 
                              object)
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

    This check will fail with decorators unless they preserve type signature.
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

def checkABC(cls):
    for base in cls.__mro__:
        if hasattr(cls, '__abstractmethods__'):
            implements(base, cls)
    return cls

class ABC:
    """
    Base class for abstract base classes.

    Inherit from this class to create an ABC which checks type signatures
    and implements issubclass and isinstance with respect to the base
    class, even if the subclass is implemented with duck typing rather
    than inheritance.

    Use the @checkABC decorator to check that the class implements the ABC.
    """
    __metaclass__ = abc.ABCMeta
    @classmethod
    def __subclasshook__(cls, C):
        """
        Allow isinstance and issubclass to be used.
        """
        #print "subclass check",cls,C
        try:
            if implements(cls, C): return True
        except NotImplementedError:
            return False


def test():
    class A(object):
        """
        Template defined by the usual python class definition
        """
        color = 'red'
        def a(self, a, b, c=2, *args, **kw): pass
    class pyABC(object):
        """
        Template defined by the awkward python ABC definition
        """
        __metaclass__ = abc.ABCMeta
        color = 'red'
        @abc.abstractmethod
        def a(self, a, b, c=2, *args, **kw): pass
        def b(self): pass
        @classmethod
        def __subclasshook__(cls, C):
            """
            Allow isinstance and issubclass to be used.
            """
            try:
                if cls is pyABC and implements(pyABC, C): return True
            except NotImplementedError:
                return False
    class myABC(ABC):
        color = 'red'
        @abc.abstractmethod
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
    class E(pyABC):
        def a(self, a, b, c=2, *varargs, **kw): pass
    class F(myABC):
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
    class E_bad_sig(pyABC):
        def a(self): pass
    class E_missing(pyABC):
        pass
    class F_bad_sig(myABC):
        def a(self): pass
    class F_missing(myABC):
        pass

    for cls in B,C,D,E,F:
        #print "should pass",cls
        implements(A, cls)
        implements(pyABC, cls)
        implements(myABC, cls)
        implements(Mixin, cls)
        assert issubclass(cls, pyABC)
        assert issubclass(cls, myABC)
        obj = cls()
        assert isinstance(obj, pyABC)
        assert isinstance(obj, myABC)

    for cls in (B_not_type, B_not_def, B_missing_attribute, B_missing_arg,
                B_extra_arg, B_missing_varargs, B_missing_keywords,
                dict, unicode, set, list, tuple, int, float, bool,
                E_bad_sig, E_missing, F_bad_sig, F_missing):
        #print "should fail",cls
        assert not issubclass(cls, pyABC)
        assert not issubclass(cls, myABC)
        try:
            obj = cls()
            assert not isinstance(obj, pyABC)
            assert not isinstance(obj, myABC)
        except TypeError: 
            pass
        for base in (A, pyABC, myABC, Mixin):
            try:
                implements(base, cls)
                raise Exception("implements(%s,%s) did not raise exception"
                                % (base.__name__,cls.__name__))
            except NotImplementedError:
                pass

    # Decorator checks
    @checkABC
    class CheckedPyABC(pyABC):
        color = 'blue'
        def a(self, a, b, c=2, *varargs, **keywords): pass
    assert isinstance(CheckedPyABC(), pyABC)

    @checkABC
    class CheckedMyABC(myABC):
        color = 'blue'
        def a(self, a, b, c=2, *varargs, **keywords): pass
    assert isinstance(CheckedMyABC(), pyABC)

    @implements(A)
    class ADecorator(object):
        color = 'blue'
        def a(self, a, b, c=2, *varargs, **keywords): pass

    try:
        @implements(A)
        class notADecorator(object):
            color = 3
        @checkABC
        class FailedPyABC(pyABC):
            color = 3
        raise Exception("exception not raised")
    except NotImplementedError:
        pass

    
if __name__ == "__main__":
    test()
