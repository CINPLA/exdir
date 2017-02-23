if [ $TRAVIS_TEST_RESULT -eq 0 ]; then
    PACKAGE=$(conda build -c conda-forge . --output --python $TRAVIS_PYTHON_VERSION)
    echo "Package name $PACKAGE"
    conda convert $PACKAGE --platform all -o packages
    cd packages
    for os in $(ls); do
        cd $os
        for package in $(ls); do
            echo "Uploading $package to anaconda with anaconda upload..."
            set +x # hide token
            anaconda -t "$CONDA_UPLOAD_TOKEN" upload -u "$1" --force $package
            set -x
        done
        cd ..
    done
    cd ..
    echo "Upload command complete!"
else
    echo "Upload cancelled due to failed test."
fi
