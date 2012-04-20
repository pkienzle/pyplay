import quack
from base import PluginBase, PluginDucktype

class BadImplementation(PluginBase):

    def load(self, input):
        return input.read()

    def save(self, output):
        return output.write("no data")

try:
    quack.implements(PluginBase,BadImplementation)
except Exception,e:
    print "Bad1:",e

# Decorator form
try:
    @quack.implements(PluginBase)
    class BadImplementation2(PluginBase):

        def load(self, input):
            return input.read()

        def save(self, output):
            return output.write("no data")
except Exception,e:
    print "Bad2:", e

# Quack should work for missing, but doesn't
try:
    @quack.implements(PluginBase)
    class MissingABC(PluginBase):
        def load(self, input):
            return input.read()
        def _save(self, output, data):
            return output.write(data)
    print "Incorrect success with missing method when using quack with ABC"
except Exception,e:
    print "Missing:", e

# Quack should work for missing, but doesn't
try:
    @quack.implements(PluginDucktype)
    class MissingDucktype(object):
        def load(self, input):
            return input.read()
        def _save(self, output, data):
            return output.write(data)
    print "Incorrect success with missing method when using quack with Ducktype"
except Exception,e:
    print "Missing:", e

@quack.implements(PluginBase)
class GoodABCImpl(PluginBase):
    def load(self, input):
        return input.read()
    def save(self, output, data):
        return output.write(data)

@quack.implements(PluginBase)
class GoodDucktypeImpl(object):
    def load(self, input):
        return input.read()
    def save(self, output, data):
        return output.write(data)

