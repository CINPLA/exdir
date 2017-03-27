mkdir -p "$CONDA_BLD_PATH"
conda config --set anaconda_upload no
conda build . $CONDA_CHANNELS --python "$TRAVIS_PYTHON_VERSION" --dirty
