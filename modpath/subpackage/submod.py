print "submod __name__", __name__

def fn():
    print "From within function, use function_name.__module__ to get", fn.__module__
    pass

