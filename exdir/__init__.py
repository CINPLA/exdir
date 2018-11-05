from . import core
from . import plugin_interface
from . import plugins
from .core import File, validation, Attribute, Dataset, Group, Raw, Object

# TODO remove versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Jupyter extensions
def _jupyter_server_extension_paths():
    return [{
        "module": "exdir"
    }]

# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        # the path is relative to the `exdir` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="exdir",
        # _also_ in the `nbextension/` namespace
        require="exdir/index")]

def load_jupyter_server_extension(nbapp):
    nbapp.log.info("Exdir extension enabled!")
