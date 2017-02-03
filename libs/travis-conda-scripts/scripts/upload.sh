PACKAGE=$(conda build -c conda-forge . --output)
echo "Package name $PACKAGE"
set +x
anaconda -t "$CONDA_UPLOAD_TOKEN" upload -u cinpla --force $PACKAGE
