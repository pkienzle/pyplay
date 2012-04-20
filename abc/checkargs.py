import quack
from base import PluginBase, PluginDucktype

class BadImplementation(PluginBase):

    def load(self, input):
        return input.read()

    def save(self, output):
        return output.write("no data")

try:
    quack.check_class(PluginBase,BadImplementation)
except Exception,e:
    print "Bad1:",e

# Decorator form
try:
    @quack.check_class(PluginBase)
    class BadImplementation2(PluginBase):

        def load(self, input):
            return input.read()

        def save(self, output):
            return output.write("no data")
except Exception,e:
    print "Bad2:", e

# Quack should work for missing, but doesn't
try:
    @quack.check_class(PluginBase)
    class MissingImplementation(PluginBase):
        def load(self, input):
            return input.read()
        def _save(self, output, data):
            return output.write(data)
    print "Incorrect success with missing method when using quack with ABC"
except Exception,e:
    print "Missing:", e

# Quack should work for missing, but doesn't
try:
    @quack.check_class(PluginDucktype)
    class MissingDucktypeImplementation(PluginDucktype):
        def load(self, input):
            return input.read()
        def _save(self, output, data):
            return output.write(data)
    print "Incorrect success with missing method when using quack with Ducktype"
except Exception,e:
    print "Missing:", e

@quack.check_class(PluginBase)
class GoodImplementation(PluginBase):
    def load(self, input):
        return input.read()
    def save(self, output, data):
        return output.write(data)


if __name__ == '__main__':
    print 'Subclass:', issubclass(GoodImplementation, PluginBase)
    print 'Instance:', isinstance(GoodImplementation(), PluginBase)
