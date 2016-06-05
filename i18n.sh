#!/usr/bin/env bash
#

# Say no to errors
set -e

domain="deform"
py=python
if [[ -f $INS/bin/pyramidpy ]];then
    py="$INS/bin/pyramidpy"
fi

# $py setup.py  extract_messages
# $py setup.py  update_catalog -D $domain
# $py setup.py  compile_catalog -D $domain
pot-create -c lingua.ini deform


