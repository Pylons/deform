#!/bin/bash
# Usage:
#     Initial catalog creation (lang is the language identifier):
#         ./i18n.sh lang
#     Updating translation and compile catalog:
#         ./i18n.sh

# configuration
DOMAIN="deform"
SEARCH_PATH="$DOMAIN/"
LOCALES_PATH="$DOMAIN/locale"
# end configuration

# create locales folder if not exists
if [ ! -d "$LOCALES_PATH" ]; then
    echo "Locales directory not exists, create"
    mkdir -p "$LOCALES_PATH"
fi

# create pot if not exists
if [ ! -f "$LOCALES_PATH"/$DOMAIN.pot ]; then
    echo "Create pot file"
    touch "$LOCALES_PATH"/$DOMAIN.pot
fi

# no arguments, extract and update
if [ $# -eq 0 ]; then
    echo "Extract messages"
    pot-create "$SEARCH_PATH" -o "$LOCALES_PATH"/$DOMAIN.pot

    echo "Update translations"
    for po in "$LOCALES_PATH"/*/LC_MESSAGES/$DOMAIN.po; do
        msgmerge -o "$po" "$po" "$LOCALES_PATH"/$DOMAIN.pot
    done

    echo "Compile message catalogs"
    for po in "$LOCALES_PATH"/*/LC_MESSAGES/*.po; do
        lg=${po##$LOCALES_PATH/}
        lg=${lg%%/LC_MESSAGES/*}
        echo -n "$lg: "
        msgfmt --statistics -o "${po%.*}.mo" "$po"
    done

# first argument represents language identifier, create catalog
else
    cd "$LOCALES_PATH"
    mkdir -p $1/LC_MESSAGES
    msginit -i $DOMAIN.pot -o $1/LC_MESSAGES/$DOMAIN.po -l $1
fi
