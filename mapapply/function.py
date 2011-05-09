import multiprocessing

def f(a,b):
    return a*b
def g(a,b,c):
    return a*b+c

class Sample(object):
    def __init__(self, base):
        self.base=base
    def g(self, a,b,c):
        return a*b+c + self.base
    def f(self, a,b):
        return self.base+a+b
    __call__ = f

class CallWrapper(object):
    def __init__(self, object, methodname):
        self.object = object
        self.methodname = methodname
    def __call__(self, *args):
        return getattr(self.object,self.methodname)(*args)

def mapapply(fplusargs): 
    return apply(fplusargs[0],fplusargs[1:])

if __name__ == "__main__":
    pool = multiprocessing.Pool()
    print pool.map(mapapply,zip((f,f,f),(1,2,3),(4,5,6)))
    print pool.map(mapapply,zip((g,g,g),(1,2,3),(4,5,6),(7,8,9)))
    s100 = Sample(100)
    s200 = Sample(200)
    print pool.map(mapapply,((f,1,2),(g,1,2,3),(f,3,4),(s100, 3, 4),(s100, 4, 5),(s200, 3, 4),
                             (CallWrapper(s200,'g'),1,2,3)))
