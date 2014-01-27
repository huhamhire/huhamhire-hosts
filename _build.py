#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _build.py : Tools to make packages for different platforms
#
# Copyleft (C) 2014 - huhamhire hosts team <hosts@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING
# THE WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import os
import sys
import shutil

from __version__ import __version__

SCRIPT = "hoststool.py"

SCRIPT_DIR = os.getcwd() + '/'
RELEASE_DIR = "../release/"
# Shared package settings and metadata
NAME = "HostsUtl"
VERSION = __version__
DESCRIPTION = "HostsUtl - Hosts Setup Utility"
AUTHOR = "Hamhire Hu"
AUTHOR_EMAIL = "hosts@huhamhire.com",
LICENSE = "Public Domain, Python, BSD, GPLv3 (see LICENSE)",
URL = "https://hosts.huhamhire.com",
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: MacOS X",
    "Environment :: Win32 (MS Windows)",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Other Audience",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Python Software Foundation License",
    "License :: OSI Approved :: BSD License",
    "License :: OSI Approved :: GNU General Public License v3",
    "License :: Public Domain",
    "Natural Language :: English",
    "Natural Language :: Chinese (Simplified)",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Topic :: Communications",
    "Topic :: Database",
    "Topic :: Desktop Environment",
    "Topic :: Documentation",
    "Topic :: Internet :: Name Service (DNS)",
    "Topic :: System :: Networking",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing",
    "Topic :: CommonUtil",
]
DATA_FILES = [
    ("gui/lang", [
        "gui/lang/en_US.qm",
        "gui/lang/zh_CN.qm",
        "gui/lang/zh_TW.qm",
    ]),
    ("gui/theme", [
        "gui/theme/default.qss",
    ]),
    (".", [
        "LICENSE",
        "README.rst",
        "network.conf",
    ]),
]

if sys.argv > 1:
    tar_flag = 0
    includes = []
    excludes = []
    file_path = lambda rel_path: SCRIPT_DIR + rel_path
    if sys.argv[1] == "py2tar":
        # Pack up script package for Linux users
        includes = [
            "*.py",
            "gui/lang/*.qm",
            "gui/theme/*.qss",
            "*/*.py",
            "LICENSE",
            "README.rst",
            "network.conf",
        ]
        excludes = [
            "_build.py",
            "_pylupdate4.py",
            "_pyuic4.py",
            ".gitattributes",
            ".gitignore",
        ]
        ex_files = []
        prefix = "HostsTool-x11-gpl-"
        tar_flag = 1

    elif sys.argv[1] == "py2source":
        # Pack up source package for Linux users
        includes = ["*"]
        excludes = [
            ".gitattributes",
            ".gitignore",
            "hostslist.data",
        ]
        ex_files = []
        prefix = "HostsTool-source-gpl-"
        tar_flag = 1
    else:
        prefix = "Error"
        ex_files = []

    if tar_flag:
        import glob
        import tarfile

        TAR_NAME = prefix + VERSION + ".tar.gz"
        RELEASE_PATH = RELEASE_DIR + TAR_NAME
        if not os.path.exists(RELEASE_DIR):
            os.mkdir(RELEASE_DIR)
        if os.path.isfile(RELEASE_PATH):
            os.remove(RELEASE_PATH)
        rel_len = len(SCRIPT_DIR)
        tar = tarfile.open(RELEASE_PATH, "w|gz")
        for name_format in excludes:
            ex_files.extend(glob.glob(file_path(name_format)))
        for name_format in includes:
            files = glob.glob(file_path(name_format))
            for src_file in files:
                if src_file not in ex_files:
                    tar_path = os.path.join(prefix + VERSION,
                                            src_file[rel_len:])
                    tar.add(src_file, tar_path)
                    print "compressing: %s" % src_file
        tar.close()
        exit(1)

from util import CommonUtil

system = CommonUtil.check_platform()[0]
if system == "Windows":
    # Build binary executables for Windows
    import struct
    import zipfile
    from distutils.core import setup
    import py2exe

    # Set working directories
    WORK_DIR = SCRIPT_DIR + "work/"
    DIR_NAME = "HostsTool"
    DIST_DIR = WORK_DIR + DIR_NAME + '/'
    WIN_OPTIONS = {
        "includes": ["sip"],
        "excludes": ["_scproxy", "_sysconfigdata"],
        "dll_excludes": ["MSVCP90.dll"],
        "dist_dir": DIST_DIR,
        "compressed": 1,
        "optimize": 2,
    }
    # Clean work space before build
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    # Build Executable
    print " Building Executable ".center(78, '=')
    EXE_NAME = SCRIPT.split(".")[0]
    setup(
        name=NAME,
        version=VERSION,
        options={"py2exe": WIN_OPTIONS},
        console=[
            {"script": SCRIPT,
             "dest_base": "hoststool_tui",
             "uac_info": "highestAvailable",
            },
        ],
        windows=[
            {"script": SCRIPT,
             "icon_resources": [(1, "res/img/icons/hosts_utl.ico")],
             "dest_base": EXE_NAME,
             "uac_info": "highestAvailable",
            },
        ],
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        license=LICENSE,
        url=URL,
        zipfile="lib/shared.lib",
        data_files=DATA_FILES,
        classifiers=CLASSIFIERS,
    )
    # Clean work directory after build
    shutil.rmtree(SCRIPT_DIR + "build/")
    # Pack up executable to ZIP file
    print " Compressing to ZIP ".center(78, '=')
    if struct.calcsize("P") * 8 == 64:
        PLAT = "x64"
    elif struct.calcsize("P") * 8 == 32:
        PLAT = "x86"
    else:
        PLAT = "unknown"
    DIR_NAME = DIR_NAME + '-win-gpl-' + VERSION + '-' + PLAT
    ZIP_NAME = DIR_NAME + ".zip"
    ZIP_FILE = WORK_DIR + ZIP_NAME
    compressed = zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(DIST_DIR):
        rel_path = os.path.relpath(root, os.path.dirname(DIST_DIR))
        for name in files:
            print "compressing: %s" % os.path.join(root, name)
            compressed.write(
                os.path.join(root, name),
                os.path.join(DIR_NAME, rel_path, name))
    compressed.close()
    # Move ZIP file to release directory
    RELEASE_PATH = RELEASE_DIR + ZIP_NAME
    if not os.path.exists(RELEASE_DIR):
        os.mkdir(RELEASE_DIR)
    if os.path.isfile(RELEASE_PATH):
        os.remove(RELEASE_PATH)
    shutil.move(ZIP_FILE, RELEASE_PATH)
    shutil.rmtree(WORK_DIR)
    print "Done!"

elif system == "OS X":
    # Build binary executables for Mac OS X
    from setuptools import setup
    # Set working directories
    WORK_DIR = SCRIPT_DIR + "work/"
    RES_DIR = SCRIPT_DIR + "res/mac/"
    APP_NAME = "HostsTool.app"
    APP_PATH = WORK_DIR + APP_NAME
    DIST_DIR = APP_PATH + "/Contents/"
    # Set build configuration
    MAC_OPTIONS = {
        "iconfile": "res/img/icons/hosts_utl.icns",
        "includes": ["sip", "PyQt4.QtCore", "PyQt4.QtGui"],
        "excludes": [
            "PyQt4.QtDBus",
            "PyQt4.QtDeclarative",
            "PyQt4.QtDesigner",
            "PyQt4.QtHelp",
            "PyQt4.QtMultimedia",
            "PyQt4.QtNetwork",
            "PyQt4.QtOpenGL",
            "PyQt4.QtScript",
            "PyQt4.QtScriptTools",
            "PyQt4.QtSql",
            "PyQt4.QtSvg",
            "PyQt4.QtTest",
            "PyQt4.QtWebKit",
            "PyQt4.QtXml",
            "PyQt4.QtXmlPatterns",
            "PyQt4.phonon"],
        "compressed": 1,
        "dist_dir": DIST_DIR,
        "optimize": 2,
        "plist": {
            "CFBundleAllowMixedLocalizations": True,
            "CFBundleSignature": "hamh",
            "CFBundleIdentifier": "org.pythonmac.huhamhire.HostsTool",
            "NSHumanReadableCopyright": "(C) 2014, huhamhire hosts Team"}
    }
    # Clean work space before build
    if os.path.exists(APP_PATH):
        shutil.rmtree(APP_PATH)
    if not os.path.exists(WORK_DIR):
        os.mkdir(WORK_DIR)
        # Make daemon APP
    OSAC_CMD = "osacompile -o %s %sHostsUtl.scpt" % (APP_PATH, RES_DIR)
    os.system(OSAC_CMD)
    # Build APP
    print " Building Application ".center(78, '=')
    setup(
        app=[SCRIPT],
        name=NAME,
        version=VERSION,
        options={"py2app": MAC_OPTIONS},
        setup_requires=["py2app"],
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        license=LICENSE,
        url=URL,
        data_files=DATA_FILES,
        classifiers=CLASSIFIERS,
    )
    # Clean work directory after build
    os.remove(DIST_DIR + "Resources/applet.icns")
    shutil.copy2(
        SCRIPT_DIR + "res/img/icons/hosts_utl.icns",
        DIST_DIR + "Resources/applet.icns")
    shutil.copy2(RES_DIR + "Info.plist", DIST_DIR + "Info.plist")
    shutil.rmtree(SCRIPT_DIR + "build/")
    # Pack APP to DMG file
    VDMG_DIR = WORK_DIR + "package_vdmg/"
    DMG_TMP = WORK_DIR + "pack_tmp.dmg"
    DMG_RES_DIR = RES_DIR + "dmg/"
    VOL_NAME = "HostsTool"
    DMG_NAME = VOL_NAME + "-mac-gpl-" + VERSION + ".dmg"
    DMG_PATH = WORK_DIR + DMG_NAME
    # Clean work space before pack up
    if os.path.exists(VDMG_DIR):
        shutil.rmtree(VDMG_DIR)
    if os.path.isfile(DMG_TMP):
        os.remove(DMG_TMP)
    if os.path.isfile(DMG_PATH):
        os.remove(DMG_PATH)
        # Prepare files in DMG package
    os.mkdir(VDMG_DIR)
    shutil.move(APP_PATH, VDMG_DIR)
    os.symlink("/Applications", VDMG_DIR + " ")
    shutil.copy2(DMG_RES_DIR + "background.png", VDMG_DIR + ".background.png")
    shutil.copy2(DMG_RES_DIR + "DS_Store_dmg", VDMG_DIR + ".DS_Store")
    # Make DMG file
    print " Making DMG Package ".center(78, '=')
    MK_CMD = (
        "hdiutil makehybrid -hfs -hfs-volume-name %s "
        "-hfs-openfolder %s %s -o %s" % (
            VOL_NAME, VDMG_DIR, VDMG_DIR, DMG_TMP))
    PACK_CMD = "hdiutil convert -format UDZO %s -o %s" % (DMG_TMP, DMG_PATH)
    os.system(MK_CMD)
    os.system(PACK_CMD)
    # Clean work directory after make DMG package
    shutil.rmtree(VDMG_DIR)
    os.remove(DMG_TMP)
    # Move DMG file to release directory
    RELEASE_PATH = RELEASE_DIR + DMG_NAME
    if not os.path.exists(RELEASE_DIR):
        os.mkdir(RELEASE_DIR)
    if os.path.isfile(RELEASE_PATH):
        os.remove(RELEASE_PATH)
    print "moving DMG file to: %s" % RELEASE_PATH
    shutil.move(DMG_PATH, RELEASE_PATH)
    shutil.rmtree(WORK_DIR)
    print "Done!"
