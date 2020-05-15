# (c) 2016 Anaconda, Inc. / https://anaconda.com
# All Rights Reserved
#
# conda_bundle is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.

import re
import sys
import hashlib
from os.path import normpath
from os import sep


def filename_dist(dist):
    """ Return the filename of a distribution. """
    if hasattr(dist, 'to_filename'):
        return dist.to_filename()
    else:
        return dist


def fill_template(data, d):
    pat = re.compile(r'__(\w+)__')

    def replace(match):
        key = match.group(1)
        return d[key]

    return pat.sub(replace, data)


def md5_files(paths):
    h = hashlib.new('md5')
    for path in paths:
        with open(path, 'rb') as fi:
            while True:
                chunk = fi.read(262144)
                if not chunk:
                    break
                h.update(chunk)
    return h.hexdigest()


def make_VIProductVersion(version):
    """
    always create a version of the form X.X.X.X
    """
    pat = re.compile('\d+$')
    res = []
    for part in version.split('.'):
        if pat.match(part):
            res.append(part)
    while len(res) < 4:
        res.append('0')
    return '.'.join(res[:4])


def read_ascii_only(path):
    with open(path) as fi:
        data = fi.read()
    for c in data:
        if ord(c) > 127:
            sys.exit("Error: unexpected non-ASCII character '%s' in: %s" %
                     (c, path))
    return data


if_pat = re.compile(r'^#if ([ \S]+)$\n'
                    r'(.*?)'
                    r'(^#else\s*$\n(.*?))?'
                    r'^#endif\s*$\n', re.M | re.S)
def preprocess(data, namespace):

    def if_repl(match):
        cond = match.group(1).strip()
        if eval(cond, namespace, {}):
            return match.group(2)
        else:
            return match.group(4) or ''

    return if_pat.sub(if_repl, data)


def add_condarc(info):
    if info.get('write_condarc'):
        default_channels = info.get('conda_default_channels')
        channels = info.get('channels')
        if sys.platform == 'win32':
            if default_channels or channels:
                yield '# ----- add condarc'
                yield 'Var /Global CONDARC'
                yield 'FileOpen $CONDARC "$INSTDIR\.condarc" w'
                if default_channels:
                    yield 'FileWrite $CONDARC "default_channels:$\\r$\\n"'
                    for url in default_channels:
                        yield 'FileWrite $CONDARC "  - %s$\\r$\\n"' % url
                if channels:
                    yield 'FileWrite $CONDARC "channels:$\\r$\\n"'
                    for url in channels:
                        yield 'FileWrite $CONDARC "  - %s$\\r$\\n"' % url
                yield 'FileClose $CONDARC'
        else:
            if default_channels or channels:
                yield '# ----- add condarc'
                yield 'cat <<EOF >$PREFIX/.condarc'
                if default_channels:
                    yield 'default_channels:'
                    for url in default_channels:
                        yield '  - %s' % url
                if channels:
                    yield 'channels:'
                    for url in channels:
                        yield '  - %s' % url
                yield 'EOF'
    else:
        yield ''


def get_final_url(info, url):
    mapping = info.get('channels_remap', [])
    for entry in mapping:
        src = entry['src']
        dst = entry['dest']
        if url.startswith(src):
            new_url = url.replace(src, dst)
            if url.endswith(".tar.bz2"):
              print("WARNING: You need to make the package {} available "
                    "at {}".format(url.rsplit('/', 1)[1], new_url))
            return new_url
    return url


def get_final_channels(info):
    mapped_channels = []
    for channel in info.get('channels', []):
        url = get_final_url(info, channel)
        if url.startswith("file://"):
            print("WARNING: local channel {} does not have a remap. "
                  "It will not be included in the installer".format(url))
            continue
        mapped_channels.append(url)
    return mapped_channels

def normalize_path(path):
    new_path = normpath(path)
    return new_path.replace(sep + sep, sep)


