"""
We have several situations where we want to map over a set of inputs.

(f1, (1,2,3)) => [f1(1), f1(2), f1(3)]
(f2, ((1,2),(3,4),(5,6)) => [f2(1,2), f2(3,4), f2(5,6)]
((f2,1,2),(f3,3,4,5),(f2,6,7)) => [f2(1,2), f3(3,4,5), f2(6,7)]

Repeat for f1,f2 callable object

Repeat for f1,f2 method of an object
"""
import multiprocessing

class ApplyMethod(object):
    """ Pickleable method reference

    Make a method reference pickleable by storing its object and
    its method name.  This will expand as a callable when unpickled.
    """
    def __init__(self, method):
        self.object = method.__self__
        self.methodname = method.__name__
    def __call__(self, *args, **kw):
        return getattr(self.object,self.methodname)(*args, **kw)

class MapApplyMethod(object):
    """ Pickleable method reference

    Make a method reference pickleable by storing its object and
    its method name.  This will expand as a callable when unpickled.
    """
    def __init__(self, method):
        self.object = method.__self__
        self.methodname = method.__name__
    def __call__(self, *args, **kw):
        return apply(getattr(self.object,self.methodname), *args, **kw)

class Apply(object):
    """
    Pickleable function application

    Make a function apply reference pickleable.
    """
    def __init__(self, function):
        self.function = function
    def __call__(self, *args, **kw):
        return apply(self.function, *args, **kw)

def mapapply(fplusargs): 
    """
    Apply a function to a set of arguments.

    mapapply( (f, a, b, c) ) returns f(a, b c)
    """
    return apply(fplusargs[0],fplusargs[1:])

# ==============================

# Some sample functions, with variable number of arguments
def f1(a):
    return a*a
def f2(a,b):
    return a*b
def f3(a,b,c):
    return a*b+c

# An example class defined as a callable
class fcallable(object):
    def __init__(self, base):
        self.base=base # give it some state
    def f(self, a,b):
        return self.base+a+b
    __call__ = f

# An example class with a method we want to call
class fmethod(object):
    def __init__(self, base):
        self.base = base # give it some state
    def f1(self, a):
        return a*a + self.base
    def f2(self, a,b):
        return a*b + self.base
    def f3(self, a,b,c):
        return a*b+c + self.base

# Run some tests
if __name__ == "__main__":
    pool = multiprocessing.Pool()
    # Map f(a)
    inp = (1,2,3)
    print "1**2 2**2 3**2 =>",pool.map(f1, inp)
    # Map f(a,b)
    inp = ((1,4),(2,5),(3,6))
    print "1*4 2*5 3*6 =>",pool.map(Apply(f2),inp)

    # Map apply( (f,a,b), (g,a,b,c), ...)
    inp = ((f2,1,4),(f3,2,5,10),(f2,3,6))
    print "1*4 2*5+10 3*6 =>", pool.map(mapapply, inp)

    # Map S(a) where S is an object with __callable__
    s100 = fcallable(100)
    inp = ((1,4),(2,5),(3,6))
    print "1*4+100 2*5+100 3*6+100 =>", pool.map(Apply(s100), inp)

    # Map S.f1(a)
    s100 = fmethod(100)
    inp = (1,2,3)
    print "1**2+100 2**2+100 3**2+100 =>", pool.map(ApplyMethod(s100.f1), inp) 

    # Map S.f2(a,b)
    s100 = fmethod(100)
    inp = ((1,4),(2,5),(3,6))
    print "1*4+100 2*5+100 3*6+100 =>",pool.map(MapApplyMethod(s100.f2), inp)

    # Map apply( (s1,a,b), (s2,a,b), ...)
    s100 = fcallable(100)
    s200 = fcallable(200)
    inp = ((s100,1,4),(s200,2,5),(s100,3,6))
    print "1*4+100 2*5+200 3*6+100 =>", pool.map(mapapply, inp)

    # Map apply( (s1.f2,a,b), (s1.f3,a,b,c), ...)
    s100 = fmethod(100) 
    s200 = fmethod(200) 
    inp = ((ApplyMethod(s100.f2),1,4), (ApplyMethod(s100.f3),2,5,10),
           (ApplyMethod(s200.f2),3,6))
    print "1*4+100 2*5+10+100 3*6+200 =>", pool.map(mapapply,inp)
