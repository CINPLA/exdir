import os
import inspect

from . import core
from .core import plugin
from .core import File

# TODO remove versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

file_plugins = []
group_plugins = []
dataset_plugins = []
attribute_plugins = []

try:
    import pluginbase
    plugin_base = pluginbase.PluginBase(
        package="exdir.plugins",
        searchpath=[]
    )

    plugin_source = plugin_base.make_plugin_source(
        identifier="exdir",
        searchpath=[
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "plugins"
            )
        ]
    )

    plugin_types = [
        (dataset_plugins, core.plugin.Dataset),
        (attribute_plugins, core.plugin.Attribute),
        (attribute_plugins, core.plugin.Group),
        (attribute_plugins, core.plugin.File)
    ]

    for plugin_list, plugin_type in plugin_types:
        for plugin_name in plugin_source.list_plugins():
            plugin = plugin_source.load_plugin(plugin_name)
            classes = inspect.getmembers(plugin, inspect.isclass)
            for name, class_type in classes:
                instance = class_type()
                if isinstance(instance, plugin_type):
                    plugin_list.append(instance)

        plugin_list = sorted(plugin_list)

except ImportError:
    # TODO do not warn more than once
    print("WARNING: pluginbase not installed. No exdir plugins will be loaded.")
