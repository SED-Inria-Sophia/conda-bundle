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
from conda_env import env

THIS_DIR = dirname(__file__)

def create(info, verbose=False):
    tmp_dir_base_path = join(dirname(info['_outpath']), "tmp")
    try:
        os.makedirs(tmp_dir_base_path)
    except:
        pass
    tmp_dir = tempfile.mkdtemp(dir=tmp_dir_base_path)
        env

    os.unlink(tarball)
    os.chmod(shar_path, 0o755)

    shutil.rmtree(tmp_dir)

