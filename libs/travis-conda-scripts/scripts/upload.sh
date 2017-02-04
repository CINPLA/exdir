PACKAGE=$(conda build -c conda-forge . --output)
echo "Package name $PACKAGE"
set +x
echo "Uploading to anaconda with anaconda upload..."
anaconda -t "$CONDA_UPLOAD_TOKEN" upload -u cinpla --force $PACKAGE
set -x
