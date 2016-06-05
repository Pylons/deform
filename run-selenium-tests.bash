#!/bin/bash
#
# This will run Selenium tests against deformdemo https://github.com/Pylons/deformdemo
#
# This script assumes you have checked out deformdemo to folder deformdemo
# If there is no checkout a fresh checkout is is made. This allows you to check out
# particular PR beforehand to test against it.
#

set -u

if [ ! -e deformdemo ] ; then
    git clone git@github.com:Pylons/deformdemo.git
fi

# Locales are needed form deformdemo tests
./i18n.sh

# We need to reinstall deform with translations included
pip install -e .

# Let's go for the demo
cd deformdemo
pip install -e .

pserve demo.ini &
# http://unix.stackexchange.com/a/30371/14115
SERVER_PID=$!

nosetests -x

kill $SERVER_PID
