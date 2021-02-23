import subprocess
import exdir.plugin_interface
try:
    import pathlib
except ImportError as e:
    try:
        import pathlib2 as pathlib
    except ImportError:
        raise e
import sys

class DatasetPlugin(exdir.plugin_interface.Dataset):
    def __init__(self, verbose):
        self.verbose = verbose

    def before_load(self, dataset_path):
        path = pathlib.Path(dataset_path)
        parent_path = path.parent
        with open(dataset_path, "rb", encoding="utf-8") as f:
            test_string = b"version https://git-lfs.github.com/spec/v1"
            contents = f.read(len(test_string))
        if contents == test_string:
            command = ['git', 'rev-parse', '--show-toplevel']
            git_path = subprocess.check_output(command, cwd=str(parent_path), stderr=subprocess.STDOUT)
            git_path = pathlib.Path(git_path.decode('utf-8').rstrip())
            relative_path = path.relative_to(git_path)
            if self.verbose:
                print("Fetching Git LFS object for {}".format(relative_path))
            command = ['git', '-c', 'lfs.fetchexclude=""', 'lfs', 'pull', '-I', str(relative_path)]
            process = subprocess.Popen(command, cwd=str(git_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if self.verbose:
                while not process.poll():
                    # Git LFS has fancy loading output - this doesn't work well in Jupyter,
                    # so just replace carriage return with newline
                    contents = process.stdout.read(1).decode('utf-8').replace('\r', '\n')
                    if not contents:
                        break
                    sys.stdout.write(contents)
                    sys.stdout.flush()

            process.communicate()


class Plugin(exdir.plugin_interface.Plugin):
    def __init__(self, verbose=False):
        super(Plugin, self).__init__("git_lfs", dataset_plugins=[DatasetPlugin(verbose)])

def plugins():
    return _plugins(verbose=False)


def _plugins(verbose):
    return [
        exdir.plugin_interface.Plugin(
            "git_lfs",
            dataset_plugins=[DatasetPlugin(verbose)]
        )
    ]
