# From: http://www.doughellmann.com/PyMOTW/abc/
import abc

class PluginBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load(self, input):
        """Retrieve data from the input source and return an object."""
        return

    @abc.abstractmethod
    def save(self, output, data):
        """Save the data object to the output."""
        return

class PluginDucktype(object):

    def load(self, input):
        """Retrieve data from the input source and return an object."""
        return

    def save(self, output, data):
        """Save the data object to the output."""
        return

