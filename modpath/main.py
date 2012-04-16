from .subpackage import submod

def main():
    print "From main, use path.to.module.fn.__module__",submod.fn.__module__
    submod.fn()

if __name__ == "__main__":
    main()
