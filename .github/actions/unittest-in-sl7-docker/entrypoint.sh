#!/bin/bash -x
PYVER=${1:-"2.7"}
GITHUB_WORKSPACE=${GITHUB_WORKSPACE:-`pwd`}
export PYVER
echo PYVER=$PYVER
source decisionengine/build/scripts/utils.sh
setup_python_venv $GITHUB_WORKSPACE $PYVER
setup_dependencies
le_builddir=decisionengine/framework/logicengine/cxx/build
[ -e $le_buildir ] && rm -rf $le_builddir
mkdir $le_builddir
cd $le_builddir
cmake3 -Wno-dev --debug-output -DPYVER=$PYVER ..
make 
make liblinks
cd -
export PYTHONPATH=$PWD:$PYTHONPATH
source venv-$PYVER/bin/activate
if [ "$PYVER" == "3.6" ];then
which pytest
pytest -v --tb=native decisionengine >  ./pytest-$PYVER.log 2>&1
status=$?
else
which py.test
python -m pytest -v --tb=native decisionengine >  ./pytest-$PYVER.log 2>&1
status=$?
fi
cat ./pytest-$PYVER.log
exit $status
