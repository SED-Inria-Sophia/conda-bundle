
# Keys in `construct.yaml` file:

This document describes each of they keys in the `construct.yaml` file,
which is the main configuration file of a constructor configuration
directory.

All keys are optional, except otherwise noted.  Also, the keys `specs`
and `packages` take either a list of items, or a path to a file,
which contains one item per line (excluding lines starting with `#`).

Also note, that any line in `construct.yaml` may contain a selector at the
end, in order to allow customization for selected platforms.


## <a href="#new-keys">Jump to the new keys introduced with <b>conda-bundle<b></a>


## `name`

required: True

argument type(s): ``str``, 

Name of the installer.  May also contain uppercase letter.  The installer
name is independent of the names of any of the conda packages the installer
is composed of.

## `version`

required: True

argument type(s): ``str``, 

Version of the installer.  Just like the installer name, this version
is independent of any conda package versions contained in the installer.

## `channels`

required: False

argument type(s): ``list``, 

The conda channels from which packages are retrieved, when using the `specs`
key below, but also when using the `packages` key ,unless the full URL is
given in the `packages` list (see below).

## `channels_remap`

required: False

argument type(s): ``list``, 

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

## `specs`

required: False

argument type(s): ``list``, ``str``, 

List of package specifications, e.g. `python 2.7*`, `pyzmq` or `numpy >=1.8`.
This list of specifications if given to the conda resolver (as if you were
to create a new environment with those specs). The packages may also be
specified by their entire URL,
e.g.`https://repo.anaconda.com/pkgs/main/osx-64/openssl-1.0.2o-h26aff7b_0.tar.bz2`.

## `user_requested_specs`

required: False

argument type(s): ``list``, ``str``, 

List of package specifications to be recorded as "user-requested" for the 
initial environment in conda's history file. If not given, user-requested
specs will fall back to 'specs'. 

## `exclude`

required: False

argument type(s): ``list``, 

List of package names to be excluded, after the '`specs` have been resolved.
For example, you can say that `readline` should be excluded, even though it
is contained as a result of resolving the specs for `python 2.7`.

## `menu_packages`

required: False

argument type(s): ``list``, 

Packages for menu items will be installed (if the conda package contains the
necessary metadata in "Menu/<package name>.json").  Menu items are currently
only supported on Windows.  By default, all menu items will be installed.

## `ignore_duplicate_files`

required: False

argument type(s): ``bool``, 

By default, constructor will error out when adding packages with duplicate
files in them. Enable this option to warn instead and continue.

## `install_in_dependency_order`

required: False

argument type(s): ``bool``, 

By default the conda packages included in the created installer are installed
in alphabetical order, Python is always installed first for technical
reasons.  Using this option, the packages are installed in their dependency
order (unless the explicit list in `packages` is used).

## `conda_default_channels`

required: False

argument type(s): ``list``, 

You can list conda channels here which will be the default conda channels
of the created installer (if it includes conda).

## `installer_filename`

required: False

argument type(s): ``str``, 

The filename of the installer being created.  A reasonable default filename
will determined by the `name`, `version`, platform and installer type.

## `license_file`

required: False

argument type(s): ``str``, 

Path to the license file being displayed by the installer during the install
process.

## `keep_pkgs`

required: False

argument type(s): ``bool``, 

By default, no conda packages are preserved after running the created
installer in the `pkgs` directory.  Using this option changes the default
behavior.

## `signing_identity_name`

required: False

argument type(s): ``str``, 

By default, the MacOS pkg installer isn't signed. If an identity name is specified
using this option, it will be used to sign the installer. Note that you will need
to have a certificate and corresponding private key together called an 'identity'
in one of your accessible keychains.

## `attempt_hardlinks`

required: False

argument type(s): ``bool``, 

By default, conda packages are extracted into the root environment and then
patched. Enabling this option will result into extraction of the packages into
the `pkgs` directory and the files in the root environment will be hardlinks to
the files kept in the `pkgs` directory and then patched accordingly.

## `write_condarc`

required: False

argument type(s): ``bool``, 

By default, no .condarc file is written. If set, a .condarc file is written to
the base environment if there are any channels or conda_default_channels is set.

## `company`

required: False

argument type(s): ``str``, 

Name of the company/entity who is responsible for the installer.

## `uninstall_name`

required: False

argument type(s): ``str``, 

Application name in the Windows "Programs and Features" control panel.
Defaults to `${NAME} ${VERSION} (Python ${PYVERSION} ${ARCH})`.

## `pre_install`

required: False

argument type(s): ``str``, 

Path to a pre install (bash - Unix only) script.

## `post_install`

required: False

argument type(s): ``str``, 

Path to a post install (bash for Unix - .bat for Windows) script.

## `post_install_desc`

required: False

argument type(s): ``str``, 

Short description of the "post_install" script to be displayed as label of 
the "Do not run post install script" checkbox in the windows installer.
If used and not an empty string, the "Do not run post install script" 
checkbox will be displayed with this label.

## `pre_uninstall`

required: False

argument type(s): ``str``, 

Path to a pre uninstall (.bat for Windows) script. Only supported on Windows.

## `welcome_image`

required: False

argument type(s): ``str``, 

Path to an image (in any common image format `.png`, `.jpg`, `.tif`, etc.)
which is used as the welcome image for the Windows installer.
The image is re-sized to 164 x 314 pixels.
By default, an image is automatically generated.

## `header_image`

required: False

argument type(s): ``str``, 

Like `welcome_image` for Windows, re-sized to 150 x 57 pixels.

## `icon_image`

required: False

argument type(s): ``str``, 

Like `welcome_image` for Windows, re-sized to 256 x 256 pixels.

## `default_image_color`

required: False

argument type(s): ``str``, 

The color of the default images (when not providing explicit image files)
used on Windows.  Possible values are `red`, `green`, `blue`, `yellow`.
The default is `blue`.

## `welcome_image_text`

required: False

argument type(s): ``str``, 

If `welcome_image` is not provided, use this text when generating the image
(Windows only). Defaults to `name`.

## `header_image_text`

required: False

argument type(s): ``str``, 

If `header_image` is not provided, use this text when generating the image
(Windows only). Defaults to `name`.

<!--
## `initialize_by_default`

required: False

argument type(s): ``bool``, 

Default choice for whether to add the installation to the PATH environment
variable. The user is still able to change this during interactive
installation.

## `register_python_default`

required: False

argument type(s): ``bool``, 

Default choice for whether to register the installed Python instance as the
system's default Python. The user is still able to change this during
interactive installation. (Windows only)
-->

<a id="new-keys"></a>

# New and updated keys specific to `conda-bundle` 

## `installer_type`

required: False

argument type(s): ``str``, 

The type of the installer being created.  Possible values are "sh" and "tar.bz2" for Linux, and "exe" for Windows.  By default, the type is "sh" on Unix, and "exe" on Windows.


## `shortcuts`

required: True (on Windows)

argument types(s): ``dict``, with keys  `name (string), path (string), options (string), icon (string), terminal (bool)`


This lets you define shortcuts to be created on Windows. assuming the install folder is `__INSTALL_PATH__`:
- for Linux usually bin/myapp
- for Windows usually Library/bin/myapp.exe

The dictionary has 6 fields: `name, path, options, icon`, `terminal`. `name` and `path` are mandatory. `options`, `terminal` and `icons` are facultative. `terminal` is an option specific to Linux, set to **false** by default, that lets you open the programme within a terminal (useful to see command outputs for GUI app too)

Example:

```yaml
shortcuts:
  the_app_shortcut:
    name: "MyProgram"
    path: "__INSTALL_PATH__\\Library\\bin\\myProgram.exe" [win]
    path: "__INSTALL_PATH__/bin/myProgram" [linux]
    options: ""
    icon: "__INSTALL_PATH__\\Menu\\app.ico" [win] # You can put a system icon too, like: "$WINDIR\\System32\\Bubbles.scr"
    icon: "__INSTALL_PATH__/Menu/icon.png" [linux]
    terminal: true
  the_conda_console_shortcut:
    name: "MyProgram Prompt"
    path: "$WINDIR\\System32\\cmd.exe"
    options: "$\\\"/K$\\\" __INSTALL_PATH__\\Scripts\\activate.bat __INSTALL_PATH__"

```
Note: key names like `the_app_shortcut` or `the_conda_console_shortcut` don't matter, they could be named however you like, even `0, 1, 2`...

## `finish_link`

required: False

argument types(s): ``dict``, with keys `url, text`

A link to display at the end of the installer (for Windows installer and Linux SH installer)
    url: the url
    text: the text to be displayed

Example:
```yaml
finish_link:
    url: "https://team.gitlabpages.mycompany.fr/myproject/"
    text: "Open the project website"
```

## `win_register_shell`

required: False

argument types(s): ``bool``

whether or not to let the user to register its shell. This adds a shortcut to the right-click menu in Windows Explorer so that you can open the local Conda prompt of the project in any folder on Windows. It comes in handy if your program has many command-line tools.

## `optional_post_install`

required : False

argument type(s): ``dict``, with keys: `default (bool)`, `py_script (string, path to stript)`, `text (string)`

Post-install script that may or may not be run after installation. Could be downloading remote resources or whatnot.

example:
```yaml
optional_post_install:
  a_dummy_key_for_the_first_script:
    default: true
    py_script: "./post_install_example.py"
    text: "Run the post-install script post_install_example.py"

```

## List of available selectors:

- ``aarch64``
- ``armv7l``
- ``linux``
- ``linux32``
- ``linux64``
- ``osx``
- ``ppc64le``
- ``unix``
- ``win``
- ``win32``
- ``win64``
- ``x86``
- ``x86_64``
