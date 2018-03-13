from . import core
from . import plugin_interface
from . import plugins
from .core import File, validation

# TODO remove versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# core.plugin.load_plugins()
