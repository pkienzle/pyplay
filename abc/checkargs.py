import quack
from base import PluginBase

class SubclassImplementation(PluginBase):
    
    def load(self, input):
        return input.read()
    
    def save(self, output):
        return output.write("no data")

quack.check_class(PluginBase,SubclassImplementation)

if __name__ == '__main__':
    print 'Subclass:', issubclass(SubclassImplementation, PluginBase)
    print 'Instance:', isinstance(SubclassImplementation(), PluginBase)
