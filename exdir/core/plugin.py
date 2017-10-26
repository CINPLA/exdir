import os
import inspect

PLUGINBASE_AVAILABLE = True

try:
    import pluginbase
except ImportError:
    PLUGINBASE_AVAILABLE = False


plugin_base = pluginbase.PluginBase(
    package="exdir.plugins",
    searchpath=[]
)

plugin_source = plugin_base.make_plugin_source(
    identifier="exdir",
    searchpath=[
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "plugins"
        )
    ]
)


class Dataset:
    def prepare_read(self, value, attrs):
        """
        Overload this function in your plugin implementation.

        It receives the data from the NumPy file and the attributes from the
        YAML file.
        The plugin parses these and returns them in a reasonable format  to be
        used by the user.
        The returned value should be numeric or numpy.ndarray.
        """

        return value

    def prepare_write(self, value):
        """
        Overload this function in your plugin implementation.

        It receives the value to be parsed by the plugin and returns a value and
        attributes that are ready to be written to file.
        The returned value should be numeric or numpy.ndarray and the returned
        attributes should be a dictionary or dictionary-like.
        """

        attrs = {}
        return value, attrs


class Attribute:
    def prepare_read(self, meta_data):
        """
        Overload this function in your plugin implementation.

        It receives the meta_data from the YAML file and returns the parsed
        version of this data to be used by the user.
        The returned value should be a dictionary or dictionary-like.
        """
        return meta_data

    def prepare_write(self, meta_data):
        """
        Overload this function in your plugin implementation.

        It receives the meta_data as provided by the user and should be parsed
        by the plugin into a basic dictionary that is YAML-compatible.
        This dictionary is returned by the function.
        """
        return meta_data

class Group:
    pass


class File:
    pass



def load_plugins():
    plugin_types = [
        (dataset_plugins, Dataset),
        (attribute_plugins, Attribute),
        (attribute_plugins, Group),
        (attribute_plugins, File)
    ]

    for plugin_list, plugin_type in plugin_types:
        for plugin_name in plugin_source.list_plugins():
            plugin = plugin_source.load_plugin(plugin_name)
            classes = inspect.getmembers(plugin, inspect.isclass)
            for name, class_type in classes:
                instance = class_type()
                setattr(instance, "IDENTIFIER", plugin.IDENTIFIER)
                if isinstance(instance, plugin_type):
                    plugin_list.append(instance)

        plugin_list = sorted(plugin_list)


file_plugins = []
group_plugins = []
dataset_plugins = []
attribute_plugins = []
