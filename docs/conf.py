# -*- coding: utf-8 -*-
#
# deform documentation build configuration file
#
# This file is execfile()d with the current directory set to its containing
# dir.
#
# The contents of this file are pickled, so don't put values in the
# namespace that aren't pickleable (module imports are okay, they're
# removed automatically).
#
# All configuration values have a default value; values that are commented
# out serve to show the default value.

import sys, os, datetime
import pkg_resources

# If your extensions are in another directory, add it here. If the
# directory is relative to the documentation root, use os.path.abspath to
# make it absolute, like shown here.
#sys.path.append(os.path.abspath('some/directory'))

# Add and use Pylons theme
import pylons_sphinx_themes

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    # enable pylons_sphinx_latesturl when this branch is no longer "latest"
    # 'pylons_sphinx_latesturl',
    ]

intersphinx_mapping = {
    'colander': ('https://docs.pylonsproject.org/projects/colander/en/latest/', None),
    'pyramid': ('https://docs.pylonsproject.org/projects/pyramid/en/latest', None),
    'python': ('https://docs.python.org/3/', None),
    }

# Add any paths that contain templates here, relative to this directory.
templates_path = ['.templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General substitutions.
project = 'deform'
thisyear = datetime.datetime.now().year
copyright = '2008-%s, Agendaless Consulting' % thisyear

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
version = pkg_resources.get_distribution('deform').version

# The full version, including alpha/beta/rc tags.
release = version

# There are two options for replacing |today|: either, you set today to
# some non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
unused_docs = ['_themes/README','todo']

# List of directories, relative to source directories, that shouldn't be
# searched for source files.
#exclude_dirs = []

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'bw'


# Options for HTML output
# -----------------------

html_theme = 'pyramid'
html_theme_path = pylons_sphinx_themes.get_html_themes_path()
html_theme_options = dict(
    github_url='https://github.com/Pylons/deform',
    # On master branch and new branch still in
    # pre-release status: true; else: false.
    in_progress='false',
    # On branches previous to "latest": true; else: false.
    outdated='false',
    )

# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
#html_style = 'pylons.css'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = 'Deform Python form library v%s' % release

# A shorter title for the navigation bar.  Default is the same as
# html_title.
#html_short_title = None

# The name of an image file (within the static path) to place at the top of
# the sidebar.
#html_logo = ''

# The name of an image file (within the static path) to use as favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or
# 32x32 pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets)
# here, relative to this directory. They are copied after the builtin
# static files, so a file named "default.css" will overwrite the builtin
# "default.css".
#html_static_path = ['.static']

# If not '', a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_use_modindex = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, the reST sources are included in the HTML build as
# _sources/<name>.
#html_copy_source = True

# If true, an OpenSearch description file will be output, and all pages
# will contain a <link> tag referring to it.  The value of this option must
# be the base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'deform'

smartquotes = False

# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, document class [howto/manual]).
latex_documents = [
  ('index', 'deform.tex', 'deform Documentation',
   'Pylons Developers', 'manual'),
]

# The name of an image file (relative to this directory) to place at the
# top of the title page.
#latex_logo = ''

# For "manual" documents, if this is true, then toplevel headings are
# parts, not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True

# -- Options for Epub output ---------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = 'deform, Version %s' \
             % release
epub_author = 'Pylons Project Developers'
epub_publisher = 'Agendaless Consulting'
epub_copyright = '2011-%d' % datetime.datetime.now().year

# The language of the text. It defaults to the language option
# or en if the language is not set.
epub_language = 'en'

# The scheme of the identifier. Typical schemes are ISBN or URL.
epub_scheme = 'URL'

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
epub_identifier = 'https://docs.pylonsproject.org/projects/deform/en/latest/'

# A unique identification for the text.
epub_uid = epub_title

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_pre_files = []

# HTML files shat should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_post_files = []

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['_static/opensearch.xml', '_static/doctools.js',
    '_static/jquery.js', '_static/searchtools.js', '_static/underscore.js',
    '_static/basic.css', 'search.html', '_static/websupport.js']

# The depth of the table of contents in toc.ncx.
epub_tocdepth = 3

