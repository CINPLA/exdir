mkdir -p $CONDA_BLD_PATH
conda config --set anaconda_upload no
conda build . -c conda-forge -c cinpla --python $TRAVIS_PYTHON_VERSION
