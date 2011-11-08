#!/usr/bin/env bash

domain="deform"
py=python
if [[ -f $INS/bin/pyramidpy ]];then
    py="$INS/bin/pyramidpy"
fi
$py setup.py  extract_messages
$py setup.py  update_catalog -D $domain
$py setup.py  compile_catalog -D $domain
# vim:set et sts=4 ts=4 tw=80:
