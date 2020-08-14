# conda-bundle


<!-- 
## Build status

[![Build Status](https://travis-ci.org/conda/constructor.svg?branch=master)](https://travis-ci.org/conda/constructor)
[![Build status](https://ci.appveyor.com/api/projects/status/cxf565h1rh3v0kaq?svg=true)](https://ci.appveyor.com/project/ContinuumAnalyticsFOSS/constructor)
[![codecov](https://codecov.io/gh/conda/constructor/branch/master/graph/badge.svg)](https://codecov.io/gh/conda/constructor)
-->

## Description:

Conda-bundle is a tool which allows constructing an installer for a collection of conda packages to be shipped as a single program. It solves needed packages using user-provided specifications, and bundles those packages.  It can currently create 3 kinds of installers, which are best thought of as delivery vehicles for the bundled packages. It is a fork of conda Constructor tweaked to behave independently from any other conda installations, avoiding risky behaviours like path rewriting, shortcuts disappearing, and other nasty things.

Currently conda-bundle supports Windows and Linux.

- On Windows it builds a EXE installer with options to create shortcuts on the desktop, in the Start Menu, and additionnal shell registering,
- On Linux you can build either a tar.bz2 portable version with simple launch scripts, or an installable .sh version that creates shortcuts in the Start Menu.

macOS is currently unsupported due to Apple policy of signing every app with an Apple Developer Certificate, which hasn't been investigated for the time being.


## Installation:

`conda-bundle` can be installed into the base environment using:

    $ conda install conda-bundle

Once installed, the conda-bundle command will be available:

    $ conda bundle -h


## Usage:

The `conda-bundle` command takes an installer specification directory as its
argument.  This directory needs to contain a file `construct.yaml`,
which specifies the name of the installer, the conda channels to
pull packages from, the conda packages included in the installer etc. .
The complete list of keys in this file can be
found in <a href="./CONSTRUCT.md">CONSTRUCT.md</a>. It mainly consists in the same keys as conda constructor, with a few keys related to conda removed, and a few more additions to let the user start the given program in a natural fashion.
Also, the directory may contain some additional optional files (such as a
license file, and image files for the Windows installer).
An example is located
in <a href="./examples/dtkthemes">examples/dtkthemes</a>.


## Devel

To build or update ``README.md`` at the root of the repo you'll need jinja2 installed

```
conda install jinja2
```

and then run ``make doc``. Or invoke the script directly with ``python scripts/make_docs.py``.
