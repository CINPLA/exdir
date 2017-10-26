from . import core
from .core import plugin
from .core import File

# TODO remove versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

core.plugin.load_plugins()
