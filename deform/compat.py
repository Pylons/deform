import sys
import string
try:
    uppercase = string.uppercase
except AttributeError: # pragma: no cover
    uppercase = string.ascii_uppercase

PY3 = sys.version_info[0] == 3

if PY3: # pragma: no cover
    string_types = str,
    text_type = str
else:
    string_types = basestring,
    text_type = unicode

try:
    from StringIO import StringIO
except ImportError: # pragma: no cover
    from io import StringIO

import urllib
try:
    url_quote = urllib.quote
    url_unquote = urllib.unquote
except AttributeError: # pragma: no cover
    import urllib.parse
    url_quote = urllib.parse.quote
    url_unquote = urllib.parse.unquote
