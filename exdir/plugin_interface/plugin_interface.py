import os
import inspect


class Plugin:
    def __init__(self, name, dataset_plugins=None, attribute_plugins=None,
                 file_plugins=None, group_plugins=None, raw_plugins=None,
                 write_before=None, write_after=None,
                 read_before=None, read_after=None):
        self.name = name
        self.dataset_plugins = dataset_plugins or []
        self.attribute_plugins = attribute_plugins or []
        self.file_plugins = file_plugins or []
        self.group_plugins = group_plugins or []
        self.raw_plugins = raw_plugins or []
        self.write_after = write_after or []
        self.write_before = write_before or []
        self.read_after = read_after or []
        self.read_before = read_before or []

        plugin_lists = [
            self.dataset_plugins,
            self.attribute_plugins,
            self.file_plugins,
            self.group_plugins,
            self.raw_plugins
        ]

        for plugin_list in plugin_lists:
            for plugin in plugin_list:
                setattr(plugin, "_plugin_module", self)


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

    def write_before(self):
        """
        Overload this function to return a list of plugin names that need to
        modify the data after this plugin.
        """
        return []

    def write_after(self):
        """
        Overload this function to return a list of plugin names that need to
        modify the data before this plugin.
        """
        return []

    def read_before(self):
        """
        Overload this function to return a list of plugin names that need to
        modify the data after this plugin.
        """
        return []

    def read_after(self):
        """
        Overload this function to return a list of plugin names that need to
        modify the data before this plugin.
        """
        return []


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

    def write_before(self):
        """
        Overload this function to return a list of plugin names that need to
        modify the data after this plugin.
        """
        return []

    def write_after(self):
        """
        Overload this function to return a list of plugin names that need to
        modify the data before this plugin.
        """
        return []

    def read_before(self):
        """
        Overload this function to return a list of plugin names that need to
        modify the data after this plugin.
        """
        return []

    def read_after(self):
        """
        Overload this function to return a list of plugin names that need to
        modify the data before this plugin.
        """
        return []


class Group:
    pass


class File:
    pass


class Raw:
    pass


def solve_plugin_order(plugins, read_mode=False):
    available_plugins = plugins
    enabled_plugins = [plugin._plugin_module.name for plugin in plugins]

    plugin_map = {}
    dependency_map = {}

    for plugin in available_plugins:
        plugin_map[plugin._plugin_module.name] = plugin
        if read_mode:
            original = plugin._plugin_module.read_after
        else:
            original = plugin._plugin_module.write_after

        new_set = set()
        for other in original:
            if other in enabled_plugins:
                new_set.add(other)
        dependency_map[plugin._plugin_module.name] = new_set

    for plugin in available_plugins:
        if read_mode:
            original = plugin._plugin_module.read_before
        else:
            original = plugin._plugin_module.write_before
        for before in original:
            if before in dependency_map:
                dependency_map[before].add(plugin._plugin_module.name)

    queue = set(enabled_plugins)
    needed_plugins = set()
    while queue:
        new_queue = set()
        for name in queue:
            for dependency in dependency_map[name]:
                new_queue.add(dependency)
            needed_plugins.add(name)
        queue = new_queue

    # remove missing plugins from maps
    plugin_map = dict(
        (name, v)
        for name, v in plugin_map.items()
        if name in needed_plugins
    )
    dependency_map = dict(
        (name, v)
        for name, v in dependency_map.items()
        if name in needed_plugins
    )

    ordered_plugins = []
    while dependency_map:
        ready = [
            name
            for name, dependencies in dependency_map.items()
            if not dependencies
        ]

        if not ready:
            raise ValueError("Circular plugin dependency found!")

        for name in ready:
            del dependency_map[name]

        for dependencies in dependency_map.values():
            dependencies.difference_update(ready)

        for name in ready:
            ordered_plugins.append(plugin_map[name])

    return ordered_plugins


class Manager:
    class Ordered:
        def __init__(self, plugins):
            self.write_order = solve_plugin_order(plugins, read_mode=False)
            self.read_order = solve_plugin_order(plugins, read_mode=True)

    def __init__(self, plugins):

        file_plugins = []
        group_plugins = []
        dataset_plugins = []
        attribute_plugins = []
        raw_plugins = []

        if plugins is None:
            plugins = []

        # make iterable if not already so
        try:
            _ = (e for e in plugins)
        except TypeError:
            plugins = [plugins]

        self.plugins = []
        for plugin in plugins:
            if inspect.ismodule(plugin):
                self.plugins.extend(plugin.plugins())
            else:
                self.plugins.append(plugin)

        for plugin in self.plugins:
            dataset_plugins.extend(plugin.dataset_plugins)
            attribute_plugins.extend(plugin.attribute_plugins)
            file_plugins.extend(plugin.file_plugins)
            group_plugins.extend(plugin.group_plugins)
            raw_plugins.extend(plugin.raw_plugins)

        self.dataset_plugins = self.Ordered(dataset_plugins)
        self.attribute_plugins = self.Ordered(attribute_plugins)
        self.file_plugins = self.Ordered(file_plugins)
        self.group_plugins = self.Ordered(group_plugins)
        self.raw_plugins = self.Ordered(raw_plugins)
