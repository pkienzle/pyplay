from . import helper

def f():
    return 3

def test():
    assert f() == 3
    assert helper.g() == 4

def demo():
    print "f",f()
    print "g",helper.g()

if __name__ == "__main__": demo()
