
import os
import sys
import json

map_path = os.path.join(
    os.path.abspath(
        os.path.dirname(sys.modules[__name__].__file__)),
    'static', 'dist', 'map.json')

def get_with_dependencies(pkg):
    js = list(pkg['js'])
    css = list(pkg['css'])
    for dep_pkg in pkg['dependencies']:
        dep = get_with_dependencies(dep_pkg)
        js.extend(dep['js'])
        css.extend(dep['css'])
    return dict(js=js, css=css)

def collect_resources_for_packages(*packages):
    map_data = json.loads(open(map_path).read())
    js = []
    css = []
    for pkg in map_data['dependencies']:
        if not packages or pkg['name'] in packages:
            dep = get_with_dependencies(pkg)
            js.extend(dep['js'])
            css.extend(dep['css'])

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


