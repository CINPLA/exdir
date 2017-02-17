if [ $TRAVIS_TEST_RESULT -eq 0 ]; then
    PACKAGE=$(conda build -c conda-forge . --output)
    echo "Package name $PACKAGE"
    set +x
    echo "Uploading to anaconda with anaconda upload..."
    anaconda -t "$CONDA_UPLOAD_TOKEN" upload -u "$1" --force $PACKAGE
    echo "Upload command complete!"
    set -x
else
    echo "Upload cancelled due to failed test."
fi
