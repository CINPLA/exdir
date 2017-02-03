conda install -y conda-build anaconda-client
mkdir ~/conda-bld
conda config --set anaconda_upload no
conda build . -c conda-forge --python $TRAVIS_PYTHON_VERSION
