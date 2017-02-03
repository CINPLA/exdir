export PATH="$HOME/miniconda/bin:$PATH"
cd docs
conda install sphinx
make doctest
