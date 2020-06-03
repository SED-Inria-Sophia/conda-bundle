# (c) 2016 Anaconda, Inc. / https://anaconda.com
# All Rights Reserved
#
# conda-bundle is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.

from __future__ import absolute_import, division, print_function

import os
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
from conda_env import cli as env_cli
from conda.cli import python_api
from multiprocessing import cpu_count

THIS_DIR = dirname(__file__)

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
    print("running command: install", arg_info_channels)
    python_api.run_command('install', arg_info_channels)
    print("Installation done.")

    # 3) pack the whole thing
    print("Packing environment as tar.bz2 using %d threads.", cpu_count())
    pack(prefix=tmp_dir,
        output=info['_outpath'],
        format='tar.bz2',
        compress_level=1,
        n_threads=cpu_count())

    # os.unlink(tarball)
    # os.chmod(shar_path, 0o755)
    print("Packing done. Removing temporary dir.")
    shutil.rmtree(tmp_dir)

