#!/bin/bash
#
# This will run Selenium tests against deformdemo.
# https://github.com/Pylons/deformdemo
#
# This script assumes you have checked out deformdemo to a folder named
# `deformdemo_functional_tests`
# If there is no checkout, then a fresh checkout is made.
# This allows you to check out a particular pull request to test against it.

set -u
set -e
set -x

function cleanup()
{
    kill $SERVER_PID
    # Cleanup locales
    cd ..
    git checkout -- deform/locale/*
}

CLEAN=true

# Add the deform checkout to your PATH, assuming you installed Firefox and
# geckodriver in the same location.
export PATH="${PWD}:$PATH"

# Checkout deformdemo
if [ ! -d deformdemo_functional_tests ] ; then
    git clone -b 2.0-branch --single-branch https://github.com/pylons/deformdemo.git deformdemo_functional_tests
fi

# Locales are needed for deformdemo tests
./i18n.sh

# We need to reinstall deform with translations included
pip install -e .

# Let's go for the demo
cd deformdemo_functional_tests
pip install -e .

# Run test server
pserve demo.ini &

SERVER_PID=$!

# Even if tests crash make sure we quit pserve
trap cleanup EXIT

# Run functional test suite against test server
nosetests "$@"

exit 0
