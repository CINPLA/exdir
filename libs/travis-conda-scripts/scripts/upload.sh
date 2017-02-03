export PATH="$HOME/miniconda/bin:$PATH"
conda install -y conda-build anaconda-client
mkdir ~/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=~/conda-bld
export GIT_DESCRIBE=$(git describe --always --tags --long)
conda build . -c conda-forge --python $TRAVIS_PYTHON_VERSION
PACKAGE=$(conda build -c conda-forge . --output)
echo "Package name $PACKAGE"
anaconda -t $CONDA_UPLOAD_TOKEN upload -u cinpla --force $PACKAGE
