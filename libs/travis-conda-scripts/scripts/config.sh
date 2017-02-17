export PATH="$HOME/miniconda/bin:$PATH"
export GIT_DESCRIBE=$(git describe --always --tags --long)
export CONDA_BLD_PATH=/tmp/conda-bld
echo PATH $PATH
echo GIT_DESCRIBE $GIT_DESCRIBE
echo CONDA_BLD_PATH $CONDA_BLD_PATH
