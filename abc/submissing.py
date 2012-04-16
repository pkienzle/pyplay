from base import PluginBase

class SubclassImplementation(PluginBase):
    
    def load(self, input):
        return input.read()
    
    def _save(self, output, data):
        return output.write(data)

if __name__ == '__main__':
    print 'Subclass:', issubclass(SubclassImplementation, PluginBase)
    print 'Instance:', isinstance(SubclassImplementation(), PluginBase)

