import os
import sys
import re
import json
import datetime
import subprocess

import jinja2

PROJECTS_ROOT = '/Users/russ/Projects'

PACKAGE_JSON_TMPL = {
    'version': '0.0.0',
    'main': 'main.js',
    'scripts': {
        'build': 'browserify main.js > bundle.js',
        'watch': 'watchify main.js -o bundle.js -v',
     },
    'author': 'Russel Simmons',
    'license': 'MIT',
}

### BEGIN BORROWING FROM Python 3.4 shlex.py
_find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

def shlex_quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"
### END BORROWING

def prompt_entry(desc, default=None):
    if default:
        full_prompt = '%s [%s]: ' % (desc, default)
    else:
        full_prompt = '%s: ' % desc

    inp = raw_input(full_prompt)

    return inp if inp else default

def prompt_multi(prompt, choices):
    print prompt
    for choice in choices:
        print '-', choice
    inp = raw_input('> ')
    assert inp in choices
    return inp

def error(msg):
    print '\nERROR:', msg
    sys.exit(1)

def check_call_echo(args):
    print '$', ' '.join(shlex_quote(arg) for arg in args)
    subprocess.check_call(args)

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))))
def render_template(fname, **kwargs):
    return template_env.get_template(fname).render(**kwargs)

def render_template_to_same_filename(fname, **kwargs):
    contents = render_template(fname, **kwargs)
    with open(fname, 'w') as f:
        f.write(contents)

if __name__ == '__main__':
    # get project name
    project_name = prompt_entry('Project name (e.g. "Cool Beans")')

    # get directory/repo name
    dir_name_suggestion = project_name.lower().replace(' ', '-')
    dir_name = prompt_entry('Directory/repo name', dir_name_suggestion)

    full_dir_path = os.path.join(PROJECTS_ROOT, dir_name)

    # make sure directory doesn't already exist
    if os.path.exists(full_dir_path):
        error('Project directory %s already exists!' % full_dir_path)

    # get description
    description = prompt_entry('Brief description')

    # make project directory and cd to it
    print 'Creating %s ...' % full_dir_path
    os.mkdir(full_dir_path)
    os.chdir(full_dir_path)

    # init git repo
    check_call_echo(['git', 'init'])

    # create package.json
    print 'Creating package.json ...'
    package_json_obj = PACKAGE_JSON_TMPL.copy()
    package_json_obj['name'] = dir_name
    package_json_obj['description'] = description
    with open('package.json', 'w') as f:
        f.write(json.dumps(package_json_obj, sort_keys=True, indent=2))

    # index.js
    print 'Creating index.html ...'
    render_template_to_same_filename('index.html', project_name=project_name)

    # main.js
    print 'Creating main.css ...'
    render_template_to_same_filename('main.css')

    # main.js
    print 'Creating main.js ...'
    render_template_to_same_filename('main.js')

    # sublime text project file
    print 'Creating Sublime Text project file ...'
    stfn = dir_name + '.sublime-project'
    with open(stfn, 'w') as f:
        f.write(render_template('sublime-project'))

    # MIT license
    print 'Creating LICENSE (MIT) ...'
    render_template_to_same_filename('LICENSE', year=datetime.date.today().year)

    # TODO: .gitignore (npm_modules, sublime text stuff?)
    # TODO: README.md

    # npm install stuff
    check_call_echo(['npm', 'install', '--save-dev', 'browserify', 'watchify'])

