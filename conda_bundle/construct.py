# (c) 2016 Anaconda, Inc. / https://anaconda.com
# All Rights Reserved
#
# conda_bundle is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.

from functools import partial
from os.path import abspath, dirname
import re
import sys

try:
    import yaml
except:
    import ruamel_yaml as yaml

from conda_bundle.exceptions import (
    UnableToParse, UnableToParseMissingJinja2, YamlParsingError,
)


# list of tuples (key name, required, type, description)
KEYS = [
    ('name',                   True,  str, '''
Name of the installer.  May also contain uppercase letter.  The installer
name is independent of the names of any of the conda packages the installer
is composed of.
'''),

    ('version',                True,  str, '''
Version of the installer.  Just like the installer name, this version
is independent of any conda package versions contained in the installer.
'''),

    ('channels',               False, list, '''
The conda channels from which packages are retrieved, when using the `specs`
key below, but also when using the `packages` key ,unless the full URL is
given in the `packages` list (see below).
'''),

    ('channels_remap',         False, list, '''
List of `(src, dest)` channels, from which, channels from `src` are also
considered while running solver, but are replaced by corresponding values from
dest when writing `urls{,.txt}`. Example use:
```
channels_remap:
  -
      src: file:///tmp/a3/conda-bld
      dest: https://repo.anaconda.com/pkgs/main
  -
      src: file:///tmp/r/conda-bld
      dest: https://repo.anaconda.com/pkgs/r
```
'''),

    ('specs',                  False, (list, str), '''
List of package specifications, e.g. `python 2.7*`, `pyzmq` or `numpy >=1.8`.
This list of specifications if given to the conda resolver (as if you were
to create a new environment with those specs). The packages may also be
specified by their entire URL,
e.g.`https://repo.anaconda.com/pkgs/main/osx-64/openssl-1.0.2o-h26aff7b_0.tar.bz2`.
'''),

    ('user_requested_specs',                  False, (list, str), '''
List of package specifications to be recorded as "user-requested" for the 
initial environment in conda's history file. If not given, user-requested
specs will fall back to 'specs'. 
'''),

    ('exclude',                False, list, '''
List of package names to be excluded, after the '`specs` have been resolved.
For example, you can say that `readline` should be excluded, even though it
is contained as a result of resolving the specs for `python 2.7`.
'''),

    ('menu_packages',           False, list, '''
Packages for menu items will be installed (if the conda package contains the
necessary metadata in "Menu/<package name>.json").  Menu items are currently
only supported on Windows.  By default, all menu items will be installed.
'''),

    ('ignore_duplicate_files',  False, bool, '''
By default, conda_bundle will error out when adding packages with duplicate
files in them. Enable this option to warn instead and continue.
'''),

    ('install_in_dependency_order', False, bool, '''
By default the conda packages included in the created installer are installed
in alphabetical order, Python is always installed first for technical
reasons.  Using this option, the packages are installed in their dependency
order (unless the explicit list in `packages` is used).
'''),

    ('conda_default_channels', False, list, '''
You can list conda channels here which will be the default conda channels
of the created installer (if it includes conda).
'''),

    ('installer_filename',     False, str, '''
The filename of the installer being created.  A reasonable default filename
will determined by the `name`, `version`, platform and installer type.
'''),

    ('installer_type',     False, str, '''
The type of the installer being created.  Possible values are "sh", "pkg",
and "exe".  By default, the type is "sh" on Unix, and "exe" on Windows.
'''),

    ('license_file',           False, str, '''
Path to the license file being displayed by the installer during the install
process.
'''),

    ('keep_pkgs',              False, bool, '''
By default, no conda packages are preserved after running the created
installer in the `pkgs` directory.  Using this option changes the default
behavior.
'''),

    ('signing_identity_name',  False, str, '''
By default, the MacOS pkg installer isn't signed. If an identity name is specified
using this option, it will be used to sign the installer. Note that you will need
to have a certificate and corresponding private key together called an 'identity'
in one of your accessible keychains.
'''),

    ('attempt_hardlinks',          False, bool, '''
By default, conda packages are extracted into the root environment and then
patched. Enabling this option will result into extraction of the packages into
the `pkgs` directory and the files in the root environment will be hardlinks to
the files kept in the `pkgs` directory and then patched accordingly.
'''),

    ('write_condarc',          False, bool, '''
By default, no .condarc file is written. If set, a .condarc file is written to
the base environment if there are any channels or conda_default_channels is set.
'''),

    ('company',                False, str, '''
Name of the company/entity who is responsible for the installer.
'''),

    ('uninstall_name',         False, str, '''
Application name in the Windows "Programs and Features" control panel.
Defaults to `${NAME} ${VERSION} (Python ${PYVERSION} ${ARCH})`.
'''),

    ('pre_install',            False, str, '''
Path to a pre install (bash - Unix only) script.
'''),

    ('post_install',           False, str, '''
Path to a post install (bash for Unix - .bat for Windows) script.
'''),

    ('post_install_desc',      False, str, '''
Short description of the "post_install" script to be displayed as label of 
the "Do not run post install script" checkbox in the windows installer.
If used and not an empty string, the "Do not run post install script"  
checkbox will be displayed with this label.
'''),

    ('pre_uninstall',          False, str, '''
Path to a pre uninstall (.bat for Windows) script. Only supported on Windows.
'''),

    ('default_prefix',         False, str, 'XXX'),

    ('welcome_image',          False, str, '''
Path to an image (in any common image format `.png`, `.jpg`, `.tif`, etc.)
which is used as the welcome image for the Windows installer.
The image is re-sized to 164 x 314 pixels.
By default, an image is automatically generated.
'''),

    ('header_image',           False, str, '''
Like `welcome_image` for Windows, re-sized to 150 x 57 pixels.
'''),

    ('icon_image',             False, str, '''
Like `welcome_image` for Windows, re-sized to 256 x 256 pixels.
'''),

    ('default_image_color',    False, str, '''
The color of the default images (when not providing explicit image files)
used on Windows.  Possible values are `red`, `green`, `blue`, `yellow`.
The default is `blue`.
'''),

    ('welcome_image_text',     False, str, '''
If `welcome_image` is not provided, use this text when generating the image
(Windows only). Defaults to `name`.
'''),

    ('header_image_text',      False, str, '''
If `header_image` is not provided, use this text when generating the image
(Windows only). Defaults to `name`.
'''),

    ('initialize_by_default',    False, bool, '''
Default choice for whether to add the installation to the PATH environment
variable. The user is still able to change this during interactive
installation.
'''),

    ('register_python_default',  False, bool, '''
Default choice for whether to register the installed Python instance as the
system's default Python. The user is still able to change this during
interactive installation. (Windows only)
'''),
]


def ns_platform(platform):
    p = platform
    return dict(
        linux = p.startswith('linux-'),
        linux32 = bool(p == 'linux-32'),
        linux64 = bool(p == 'linux-64'),
        armv7l = bool(p == 'linux-armv7l'),
        aarch64 = bool(p == 'linux-aarch64'),
        ppc64le = bool(p == 'linux-ppc64le'),
        x86 = p.endswith(('-32', '-64')),
        x86_64 = p.endswith('-64'),
        osx = p.startswith('osx-'),
        unix = p.startswith(('linux-', 'osx-')),
        win = p.startswith('win-'),
        win32 = bool(p == 'win-32'),
        win64 = bool(p == 'win-64'),
    )


sel_pat = re.compile(r'(.+?)\s*\[(.+)\]$')
def select_lines(data, namespace):
    lines = []
    for line in data.splitlines():
        line = line.rstrip()
        m = sel_pat.match(line)
        if m:
            cond = m.group(2)
            if eval(cond, namespace, {}):
                lines.append(m.group(1))
            continue
        lines.append(line)
    return '\n'.join(lines) + '\n'


# adapted from conda-build
def yamlize(data, directory, content_filter):
    data = content_filter(data)
    try:
        return yaml.safe_load(data)
    except yaml.error.YAMLError as e:
        if ('{{' not in data) and ('{%' not in data):
            raise UnableToParse(original=e)
        try:
            from conda_bundle.jinja import render_jinja
        except ImportError as ex:
            raise UnableToParseMissingJinja2(original=ex)
        data = render_jinja(data, directory, content_filter)
        return yaml.load(data)


def parse(path, platform):
    try:
        with open(path) as fi:
            data = fi.read()
    except IOError:
        sys.exit("Error: could not open '%s' for reading" % path)
    directory = dirname(path)
    content_filter = partial(select_lines, namespace=ns_platform(platform))
    try:
        res = yamlize(data, directory, content_filter)
    except YamlParsingError as e:
        sys.exit(e.error_msg())

    try:
        res['version'] = str(res['version'])
    except KeyError:
        pass

    for key in list(res):
        if res[key] is None:
            del res[key]

    return res


def verify(info):
    types_key = {} # maps key to types
    required_keys = set()
    for key, required, types, unused_descr in KEYS:
        types_key[key] = types
        if required:
            required_keys.add(key)

    for key in info:
        if key not in types_key:
            sys.exit("Error: unknown key '%s' in construct.yaml" % key)
        elt = info[key]
        types = types_key[key]
        if not isinstance(elt, types):
            sys.exit("Error: key '%s' points to %s,\n"
                     "       expected %s" % (key, type(elt), types))

    for key in required_keys:
        if key not in info:
            sys.exit("Error: Required key '%s' not found in construct.yaml" %
                     key)

    pat = re.compile(r'[\w][\w\-\.]*$')
    for key in 'name', 'version':
        value = info[key]
        if not pat.match(value) or value.endswith(('.', '-')):
            sys.exit("Error: invalid %s '%s'" % (key, value))


def generate_doc():
    print('generate_doc() is deprecated. Use scripts/make_docs.py instead')
    sys.exit(1)


if __name__ == '__main__':
    generate_doc()
