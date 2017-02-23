git fetch --unshallow  # needed to get enough commits for tag, see travis-ci/travis-ci#3412
export PATH="$HOME/miniconda/bin:$PATH"
export GIT_DESCRIBE=$(git describe --always --tags --long)
export GIT_TAG=$(git describe --always --tags --abbrev=0)
export TAG_AND_TRAVIS_BUILD=${GIT_TAG}_b${TRAVIS_BUILD_NUMBER}
export TAG_TRAVIS_BUILD_AND_COMMIT=${TAG_AND_TRAVIS_BUILD}_g${TRAVIS_COMMIT}
export CONDA_BLD_PATH=/tmp/conda-bld
echo PATH $PATH
echo GIT_DESCRIBE $GIT_DESCRIBE
echo CONDA_BLD_PATH $CONDA_BLD_PATH
echo GIT_TAG $GIT_TAG
echo TAG_AND_TRAVIS_BUILD $TAG_AND_TRAVIS_BUILD
echo TAG_TRAVIS_BUILD_AND_COMMIT $TAG_TRAVIS_BUILD_AND_COMMIT
