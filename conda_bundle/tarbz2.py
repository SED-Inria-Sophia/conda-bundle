# (c) 2016 Anaconda, Inc. / https://anaconda.com
# All Rights Reserved
#
# conda-bundle is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.

from __future__ import absolute_import, division, print_function

import os
import stat
from os.path import basename, dirname, getsize, isdir, join
import shutil
import tarfile
import tempfile

from .construct import ns_platform
from .preconda import files as preconda_files, write_files as preconda_write_files
from .utils import add_condarc, filename_dist, fill_template, md5_files, preprocess, \
    read_ascii_only, get_final_channels


from conda_pack import pack

from conda_build import environ, source, tarcheck, utils
from conda.cli import python_api
from multiprocessing import cpu_count

THIS_DIR = dirname(__file__)


def read_launch_template():
    path = join(THIS_DIR, 'launch.sh')
    print('Reading: %s' % path)
    with open(path) as fi:
        return fi.read()

def create(info, verbose=False):
    tmp_dir_base_path = join(dirname(info['_outpath']), "tmp")
    try:
        os.makedirs(tmp_dir_base_path)
    except:
        pass
    tmp_dir = tempfile.mkdtemp(dir=tmp_dir_base_path)

    # 1) create a temporary conda environment
    python_api.run_command('create', '-p', tmp_dir)
    print("temporary environment created at: %s" % tmp_dir)

    # 2) install in this temporary environment all final packages
    arg_info_channels = list()
    arg_info_channels.append('-p')
    arg_info_channels.append(tmp_dir)
    for channel in info['channels']:
        arg_info_channels.append('-c')
        arg_info_channels.append(channel)
    for package in info['specs']:
        arg_info_channels.append(package)
    print("Installing packages:", info['specs'])
    python_api.run_command('install', arg_info_channels)
    print("Installation done.")

    for t in info['shortcuts'].values():
        #for key in 'path', 'icon', 'options':
        #    if key in t:
        #        t[key] = t[key].replace("__INSTALL_PATH__", "./")
        options = ""
        icon = t['path']
        if 'options' in t:
            options = t['options']
        if 'icon' in t:
            icon = t["icon"]

        replace = {
        'NAME': info['name'],
        'name': info['name'].lower(),
        'VERSION': info['version'],
        'ENTRY_POINT': f"{t['path']} {options}"
        }
        data = read_launch_template()
        data = fill_template(data, replace)
        replace_entry = {
            'INSTALL_PATH': '.'
        }
        data = fill_template(data, replace_entry)

        with open(join(tmp_dir, f"{t['name']}.sh"), 'wb') as fo:
            fo.write(data.encode('utf-8'))
        os.chmod(join(tmp_dir, f"{t['name']}.sh"), 0o755)
    

    # 3) pack the whole thing
    archive_format = 'tar.bz2'
    print("Packing environment as %s using %d threads." % (archive_format, cpu_count()))
    pack(prefix=tmp_dir,
        output=info['_outpath'],
        format=archive_format,
        force=True,
        compress_level=1,
        n_threads=cpu_count())

    # os.unlink(tarball)
    # os.chmod(shar_path, 0o755)
    print("Packing done. Removing temporary dir.")
    shutil.rmtree(tmp_dir)