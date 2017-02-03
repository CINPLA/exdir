PACKAGE=$(conda build -c conda-forge . --output)
echo "Package name $PACKAGE"
anaconda -t $CONDA_UPLOAD_TOKEN upload -u cinpla --force $PACKAGE
