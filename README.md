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


## Devel

To start developing with conda-bundle, you need to create a conda environment on UNIX systems with:

```
conda env create -f pkg/env/conda-bundle.yaml
```

You should be able to build the recipe and create your package with:

```
conda build -c jolevy conda.recipe
```

Once you created your package, you can install it in your conda environment, and you can start tweaking the Python code directly in the install location to run it, test it, and check your changes. It should be installed in `.../lib/python3.7/site-packages/conda_bundle/` or `.../Lib/site-packages/conda_bundle` for Windows.

## Branch policy

`master` will be when we'll have a release (not anytime soon)
`develop` is the default branch for building packages at the moment
branches `windows`, `linux` and `macos` all originate from `develop`. 
You should make features in your OS branch like `windows/feature/my-cool-stuff`, then merge into branch `windows`, then when you feel ready merge into branch `develop`. This allows features to be developed on a specific OS when we need it, and you can hook your Continuous Integration to look for the right branch for the right OS.

```
Example of branch management:

-- master ---------------
-- develop----\                                                            /---develop---
               \---windows------                                          /
                \---macos---------                                       /
                 \--linux---\                               /---linux---/
                             \----linux/feature/my-stuff---/
```


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

