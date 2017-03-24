mkdir -p "$CONDA_BLD_PATH"
conda config --set anaconda_upload no
conda build . -c defaults -c conda-forge -c cinpla --python "$TRAVIS_PYTHON_VERSION" --dirty
