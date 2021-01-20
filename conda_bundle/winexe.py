# (c) 2016 Anaconda, Inc. / https://anaconda.com
# All Rights Reserved
#
# conda-bundle is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.

from __future__ import absolute_import, division, print_function

import os
from os.path import abspath, dirname, isfile, join
import shutil
from subprocess import Popen, PIPE, check_call, check_output
import sys
import math
import tempfile
import warnings

from .construct import ns_platform
from .imaging import write_images
from .install import name_dist
from .preconda import write_files as preconda_write_files
from .utils import filename_dist, fill_template, make_VIProductVersion, preprocess, add_condarc, get_final_channels

THIS_DIR = dirname(__file__)
NSIS_DIR = join(THIS_DIR, 'nsis')
MAKENSIS_EXE = join(sys.prefix, 'NSIS', 'makensis.exe')


def str_esc(s):
    for a, b in [('$', '$$'), ('"', '$\\"'), ('\n', '$\\n'), ('\t', '$\\t')]:
        s = s.replace(a, b)
    return '"%s"' % s


def read_nsi_tmpl():
    path = join(NSIS_DIR, 'main.nsi.tmpl')
    print('Reading: %s' % path)
    with open(path) as fi:
        return fi.read()


def pkg_commands(download_dir, dists, py_version, keep_pkgs, attempt_hardlinks, channels):
    for n, dist in enumerate(dists):
        fn = filename_dist(dist)
        yield ''
        yield '# --> %s <--' % fn
        yield 'File %s' % str_esc(join(download_dir, fn))

    # Set CONDA_CHANNELS to configured channels and
    # CONDA_PKGS_DIRS to the local package cache directory
    _env = 'kernel32::SetEnvironmentVariable(t,t)i("CONDA_CHANNELS", "%s").r0'%(','.join(channels))
    yield "System::Call '%s'" % _env
    _env = 'kernel32::SetEnvironmentVariable(t,t)i("CONDA_PKGS_DIRS", "$INSTDIR\pkgs").r0'
    yield "System::Call '%s'" % _env

    # Add env vars to bypass safety checks
    _env = 'kernel32::SetEnvironmentVariable(t,t)i("CONDA_SAFETY_CHECKS", "disabled").r0'
    yield "System::Call '%s'" % _env
    _env = 'kernel32::SetEnvironmentVariable(t,t)i("CONDA_EXTRA_SAFETY_CHECKS", "no").r0'
    yield "System::Call '%s'" % _env

    # Extract all the .conda and .tar.bz2 conda packages
    yield r'SetDetailsPrint TextOnly'
    yield r'DetailPrint "Setting up the package cache ..."'
    cmd = r'"$INSTDIR\_conda.exe" constructor --prefix "$INSTDIR" --extract-conda-pkgs'
    yield "nsExec::ExecToLog '%s'" % cmd
    yield "Pop $0"
    yield r'SetDetailsPrint both'

    # Install all the extracted packages
    yield r'SetDetailsPrint TextOnly'
    yield r'DetailPrint "Setting up the base environment ..."'
    cmd = r'"$INSTDIR\_conda.exe" install --offline -yp "$INSTDIR" --file "$INSTDIR\pkgs\env.txt"'
    yield "nsExec::ExecToLog '%s'" % cmd
    yield "Pop $0"
    yield r'SetDetailsPrint both'

    if not keep_pkgs:
        yield ''
        yield r'RMDir "$INSTDIR\pkgs"'


def make_nsi(info, dir_path):
    "Creates the tmp/main.nsi from the template file"
    name = info['name']
    download_dir = info['_download_dir']
    dists = info['_dists']
    py_name, py_version, unused_build = filename_dist(dists[0]).rsplit('-', 2)
    assert py_name == 'python'
    arch = int(info['_platform'].split('-')[1])
    info['post_install_desc'] = info.get('post_install_desc', "")

    start_menu_commands = ""
    desktop_commands = ""
    registry_key_commands = ""
    start_menu_delete_commands = ""
    desktop_delete_commands = ""
    registry_key_dpi_commands = "" # this will register our Qt 5.12 app in the registry to use System DPI on Windows (blurry, but scaled). Cause you know. Qt 5.12.
    post_install_commands = "" # these will be calls to the post-install scripts (python)
    post_install_files = ""

    # these are NSIS commands to create shortcuts, registry keys, and delete shortcuts.
    for t in info['shortcuts'].values():
        for key in 'path', 'icon', 'options':
            if key in t:
                t[key] = t[key].replace("__INSTALL_PATH__", "$INSTDIR")
        options = ""
        icon = t['path']
        if 'options' in t:
            options = t['options']
        if 'icon' in t:
            icon = t["icon"]
            
        start_menu_commands = start_menu_commands + 'CreateShortCut "$SMPROGRAMS\\${PRODUCT_NAME}\\' + f'{t["name"]}.lnk" "{t["path"]}" "{options}" "{icon}"\n'
        desktop_commands = desktop_commands + f'CreateShortCut "$DESKTOP\\{t["name"]}.lnk" "{t["path"]}" "{options}" "{icon}"\n'
        registry_key_commands = registry_key_commands + 'WriteRegStr ${PRODUCT_REGISTER_KEY} "${PRODUCT_DIR_REGKEY}" "" ' + f'"{t["path"]}"\n'
        start_menu_delete_commands = start_menu_delete_commands + 'Delete "$SMPROGRAMS\\${PRODUCT_NAME}' + f'\\{t["name"]}.lnk"\n'
        desktop_delete_commands = desktop_delete_commands + f'Delete "$DESKTOP\\{t["name"]}.lnk"\n'
        if t["path"].endswith(".exe") and (not t["path"].endswith("\\cmd.exe")):
            registry_key_dpi_commands = registry_key_dpi_commands + 'WriteRegStr ${PRODUCT_REGISTER_KEY} ' + f'"SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "{t["path"]}" "~ PERPROCESSSYSTEMDPIFORCEON GDIDPISCALING DPIUNAWARE"\n'

    for t in info['optional_post_install'].values():
            post_install_files = post_install_files + f"""
            File "{abspath(t["py_script"])}"\n
            """

            post_install_commands = post_install_commands + f"""
            # Note: this runs in folder $INSTDIR\conda-meta for some reason.
            
            # ${{If}} $Ana_PostInstall_State = ${{BST_CHECKED}}
                DetailPrint "Running post install: {t["py_script"]} ..."
                nsExec::ExecToLog '"$INSTDIR\pythonw.exe" -E -s "$INSTDIR\{t["py_script"]}"'
                Pop $0
            #    push 'Failed to run post install script'
            #    call AbortRetryNSExecWait
            #${{EndIf}}
            \n
            """

    
    # these appear as __<key>__ in the template, and get escaped
    replace = {
        'NAME': name,
        'VERSION': info['version'],
        'VIPV': make_VIProductVersion(info['version']),
        'COMPANY': info.get('company', 'Unknown, Inc.'),
        'ARCH': '%d-bit' % arch,
        'PY_VER': py_version[:3],
        'PYVERSION': py_version,
        'PYVERSION_JUSTDIGITS': ''.join(py_version.split('.')),
        'OUTFILE': info['_outpath'],
        'LICENSEFILE': abspath(info.get('license_file',
                               join(NSIS_DIR, 'placeholder_license.txt'))),
        'DEFAULT_PREFIX': info.get(
            'default_prefix',
            join('%LOCALAPPDATA%', name.lower())
        ),
        'POST_INSTALL_DESC': info['post_install_desc'],
    }

    if 'finish_link' in info.keys():
        replace['FINISH_LINK_URL'] = info['finish_link']['url']
        replace['FINISH_LINK_TEXT'] = info['finish_link']['text']
    else:
        replace['FINISH_LINK_URL'] = "nothing" # these keys MUST be present in dict "replace", so I put dummy in them
        replace['FINISH_LINK_TEXT'] = "nothing"


    if 'win_register_shell' in info.keys():
        replace['ALLOW_REGISTER_SHELL'] = f"{info['win_register_shell']}"
    else:
        replace['ALLOW_REGISTER_SHELL'] = "False"

    for key, fn in [('HEADERIMAGE', 'header.bmp'),
                    ('WELCOMEIMAGE', 'welcome.bmp'),
                    ('ICONFILE', 'icon.ico'),
                    ('CONDA_EXE', '_conda.exe'),
                    ('ENV_TXT', 'env.txt'),
                    ('URLS_FILE', 'urls'),
                    ('URLS_TXT_FILE', 'urls.txt'),
                    ('POST_INSTALL', 'post_install.bat'),
                    ('PRE_UNINSTALL', 'pre_uninstall.bat'),
                    ('CONDA_HISTORY', join('conda-meta', 'history')),
                    ('REPODATA_RECORD', 'repodata_record.json'),
                    ('INDEX_CACHE', 'cache')]:
        replace[key] = join(dir_path, fn)
    for key in replace:
        replace[key] = str_esc(replace[key])

    data = read_nsi_tmpl()
    ppd = ns_platform(info['_platform'])
    ppd['initialize_by_default'] = info.get('initialize_by_default', None)
    ppd['register_python_default'] = info.get('register_python_default', None)
    data = preprocess(data, ppd)
    data = fill_template(data, replace)

    cmds = pkg_commands(download_dir, dists, py_version,
                        bool(info.get('keep_pkgs')),
                        bool(info.get('attempt_hardlinks')),
                        get_final_channels(info))

    # division by 10^3 instead of 2^10 is deliberate here. gives us more room
    approx_pkgs_size_kb = int(
        math.ceil(info.get('_approx_pkgs_size', 0) / 1000))

    # these are unescaped (and unquoted)
    for key, value in [
        ('@NAME@', name),
        ('@NSIS_DIR@', NSIS_DIR),
        ('@BITS@', str(arch)),
        ('@PKG_COMMANDS@', '\n    '.join(cmds)),
        ('@WRITE_CONDARC@', '\n    '.join(add_condarc(info))),
        ('@MENU_PKGS@', ' '.join(info.get('menu_packages', []))),
        ('@SIZE@', str(approx_pkgs_size_kb)),
        ('@UNINSTALL_NAME@', info.get('uninstall_name',
            '${NAME} ${VERSION} (Python ${PYVERSION} ${ARCH})'
        )),
        ("@START_MENU_CREATE_SHORTCUT_EXE@",  start_menu_commands),
        ("@DESKTOP_CREATE_SHORTCUT_EXE@", desktop_commands),
        ("@REGISTRY_INSTDIR_KEY_EXE@", registry_key_commands),
        ("@REGISTRY_KEY_DPI_COMMANDS@", registry_key_dpi_commands),
        ("@START_MENU_DELETE_SHORTCUT_EXE@", start_menu_delete_commands),
        ("@DESKTOP_DELETE_SHORTCUT_EXE@", desktop_delete_commands),
        ("@IS_FINISH_LINK@", "" if 'finish_link' in info.keys() else "#"),
        ("@POST_INSTALL_SCRIPTS@", post_install_commands),
        ("@FILE_OPTIONAL_POST_INSTALL_SCRIPTS@", post_install_files),
        ]:
        data = data.replace(key, value)

    nsi_path = join(dir_path, 'main.nsi')
    with open(nsi_path, 'w') as fo:
        fo.write(data)
    # Copy all the NSIS header files (*.nsh)
    for fn in os.listdir(NSIS_DIR):
        if fn.endswith('.nsh'):
            shutil.copy(join(NSIS_DIR, fn),
                        join(dir_path, fn))

    print('Created %s file' % nsi_path)
    os.system(f'{nsi_path}') # yup all files are executable on Windows. It will open in your favorite text editor.
    return nsi_path


def verify_nsis_install():
    print("Checking for '%s'" % MAKENSIS_EXE)
    if not isfile(MAKENSIS_EXE):
        sys.exit("""
Error: no file %s
    please make sure nsis is installed:
    > conda install nsis
""" % MAKENSIS_EXE)
    out = check_output([MAKENSIS_EXE, '/VERSION'])
    out = out.decode('utf-8').strip()
    print("NSIS version: %s" % out)
    for dn in 'x86-unicode', 'x86-ansi', '.':
        untgz_dll = abspath(join(sys.prefix, 'NSIS',
                                 'Plugins', dn, 'untgz.dll'))
        if isfile(untgz_dll):
            break
    else:
        sys.exit("Error: no file untgz.dll")


def create(info, verbose=False):

    verify_nsis_install()
    tmp_dir = tempfile.mkdtemp()
    preconda_write_files(info, tmp_dir)
    shutil.copyfile(info['_conda_exe'], join(tmp_dir, '_conda.exe'))

    if 'pre_install' in info:
        sys.exit("Error: Cannot run pre install on Windows, sorry.\n")

    post_dst = join(tmp_dir, 'post_install.bat')
    try:
        shutil.copy(info['post_install'], post_dst)
    except KeyError:
        with open(post_dst, 'w') as fo:
            fo.write(":: this is an empty post install .bat script\n")

    pre_dst = join(tmp_dir, 'pre_uninstall.bat')
    try:
        shutil.copy(info['pre_uninstall'], pre_dst)
    except KeyError:
        with open(pre_dst, 'w') as fo:
            fo.write(":: this is an empty pre uninstall .bat script\n")

    write_images(info, tmp_dir)
    nsi = make_nsi(info, tmp_dir)
    if verbose:
        verbosity = '/V4'
    else:
        verbosity = '/V2'
    args = [MAKENSIS_EXE, verbosity, nsi]
    print('Calling: %s' % args)
    if verbose:
        sub = Popen(args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = sub.communicate()
        for msg, information in zip((stdout, stderr), ('stdout', 'stderr')):
            # on Python3 we're getting bytes
            if hasattr(msg, 'decode'):
                msg = msg.decode()
            print('makensis {}:'.format(information))
            print(msg)
    else:
        check_call(args)
    shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    make_nsi({'name': 'Maxi', 'version': '1.2',
              '_platform': 'win-64',
              '_outpath': 'dummy.exe',
              '_download_dir': 'dummy',
              '_dists': ['python-2.7.9-0.tar.bz2',
                         'vs2008_runtime-1.0-1.tar.bz2']},
             '.')
