conda install -y conda-build anaconda-client
mkdir ~/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=~/conda-bld
export BUILD_VERSION=`date +%Y%m%d`
conda build -c conda-forge .
PACKAGE=$(conda build -c conda-forge . --output)
echo "Package name $PACKAGE"
anaconda -t $CONDA_UPLOAD_TOKEN upload -u cinpla --force $PACKAGE
