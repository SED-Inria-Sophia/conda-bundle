# (c) 2016-2017 Anaconda, Inc. / http://anaconda.com
# All Rights Reserved
#
# conda_bundle is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.

import re
import sys
from os.path import abspath, dirname, join
from contextlib import contextmanager

from setuptools import setup, Distribution
from distutils.util import get_platform
try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = None

import versioneer


SETUP_PY_DIR = dirname(abspath(__file__))


def get_package_data(platform):
    platform_package_data = {
        "win32": ["nsis/*", "ttf/*"],
        "darwin": ["header.sh", "osx/*"],
        "unix": ["header.sh"],
    }
    if platform is None:
        package_data = sum(platform_package_data.values(), [])
    else:
        platform = platform if platform in platform_package_data else "unix"
        package_data = platform_package_data[platform]
    return {"conda_bundle": package_data}


class PlatformSpecificDistribution(Distribution):
    def run_commands(self):
        for cmd in self.commands:
            with self.patch_dist_data(cmd):
                self.run_command(cmd)

    @contextmanager
    def patch_dist_data(dist, cmd):
        old_have_run = dist.have_run
        old_command_obj = dist.command_obj
        old_package_data = dist.package_data
        old_has_ext_modules = dist.has_ext_modules
        try:
            # rerun everthing for top cmds since patched dist data may differ
            dist.have_run = {}
            dist.command_obj = {}
            if cmd in {"build", "install", "bdist", "bdist_egg", "bdist_wheel"}:
                # use platform dependent package data
                dist.package_data = get_package_data(sys.platform)
            if cmd in {"bdist_egg"}:
                # force platform specific build for bdist_egg
                dist.has_ext_modules = lambda: True
            yield
        finally:
            dist.have_run = old_have_run
            dist.command_obj = old_command_obj
            dist.package_data = old_package_data
            dist.has_ext_modules = old_has_ext_modules


cmdclass = versioneer.get_cmdclass()


if bdist_wheel:
    class BDistWheel(bdist_wheel):
        def finalize_options(self):
            # make wheels platform but not Python specific
            self.plat_name = self.plat_name or get_platform()
            self.universal = True
            super(BDistWheel, self).finalize_options()
    cmdclass["bdist_wheel"] = BDistWheel


setup(
    name="conda_bundle",
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    author="Anaconda, Inc.",
    author_email="conda@anaconda.com",
    url="https://github.com/SED-Inria-Sophia/conda_bundle",
    license="BSD",
    description="create installer from conda packages",
    long_description=open(join(SETUP_PY_DIR, "README.md")).read(),
    packages=["conda_bundle", "conda_bundle.tests"],
    entry_points={
        "console_scripts": ["conda_bundle=conda_bundle.main:main"],
    },
    install_requires=[
        "conda >=4.6",
        "ruamel_yaml",
        "pillow >=3.1 ; platform_system=='Windows'",
        # non-python dependency: "nsis >=3.01 ; platform_system=='Windows'",
    ],
    package_data=get_package_data(None),
    distclass=PlatformSpecificDistribution,
)
