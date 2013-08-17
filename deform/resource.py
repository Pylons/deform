
import os
import sys
import json

map_path = os.path.join(
    os.path.abspath(
        os.path.dirname(sys.modules[__name__].__file__)),
    'static', 'dist', 'map.json')

def _get_with_dependencies(pkg):
    js = list(pkg['js'])
    css = list(pkg['css'])
    for dep_pkg in pkg['dependencies']:
        dep = _get_with_dependencies(dep_pkg)
        js.extend(dep['js'])
        css.extend(dep['css'])
    return dict(js=js, css=css)


def collect_resources_for_widgets(*packages):
    """Give js and css resources needed to render a list of
    widgets in the page.

    This method uses the `static/dist/map.json` file to learn about
    installed widgets and their dependencies. This file is generated
    by process_dependencies.js based on the installation created
    by 'bower'. As such, it represents a global state of all installed
    front-end packages. Since all widgets have a `bower.json` dependency
    file, they are treated as genuine front-end packages themselves.

    The method takes a list of widget names which are typically in the
    form of "autocomplete-input-widget", the names correspond to the
    `bower.json` files created for the widgets. If the packages list are empty,
    all the widgets are selected. Otherwise only the widgets in the
    packages list _and_ all their dependencies will be selected.

    The method returns a dictionary with two fields: 'js' and 'css', each
    containing a list of resources in the order they need to be included
    from html. The resource path are relative to 'static'.
    """
    map_data = json.loads(open(map_path).read())
    js = []
    css = []
    for pkg in map_data['dependencies']:
        if not packages or pkg['name'] in packages:
            dep = _get_with_dependencies(pkg)
            js.extend(dep['js'])
            css.extend(dep['css'])
    # Reverse the order of resources, so dependencies
    # come to the front. Also make sure that each resource
    # is only included once into the list.
    js.reverse()
    unique_js = []
    for item in js:
        if item not in unique_js:
            unique_js.append(item)
    css.reverse()
    unique_css = []
    for item in css:
        if item not in unique_js:
            unique_css.append(item)
    return dict(js=unique_js, css=unique_css)


import sys

if __name__ == '__main__':
    args = sys.argv[1:]
    resources = collect_resources_for_packages(*args)
    print '***js:', resources['js']
    print '***css:', resources['css']


