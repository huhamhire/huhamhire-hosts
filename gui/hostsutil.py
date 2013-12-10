#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hostsutil.py : Main parts of Hosts Setup Utility
#
# Copyleft (C) 2013 - huhamhire hosts team <develop@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING
# THE WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE.
# =====================================================================

from zipfile import BadZipfile
from util_ui import _translate, _fromUtf8
from util import RetrieveData, CommonUtil

__version__ = "1.9.7"
__revision__ = "$Id$"
__author__ = "huhamhire <me@huhamhire.com>"

import sys

from PyQt4 import QtGui

from gui.qdialog_slots import QDialogSlots

# Path to store language files
LANG_DIR = "./gui/lang/"


class HostsUtil(QDialogSlots):
    """A class to manage the operations and UI of Hosts Setup Utility

    HostsUtil class is a subclasse of PyQt4.QtGui.QDialog which is used to
    make the main dialog of this hosts setup utility.
    This class contains a set of tools used to manage the operations while
    modifying the hosts file of current operating system. Including methods
    to manage operations to update data file, download data file, configure
    hosts, make hosts file, backup hosts file, and restore backup.
    The HostsUtil class also provides QT slots to deal with the QT singles
    emitted by the widgets on the main dialog operated by users. Extend
    methods dealing with the user interface is also given by this class.

    Attributes:
        _cur_ver (str): A string indicating the current version of hosts data
            file.
        _ipv_id (int): An integer indicating current IP version setting. The
            value could be 1 or 0. 1 represents IPv6 while 1 represents IPv4.

        _funcs (list): A list containing two lists with the information of
            function list for IPv4 and IPv6 environment.
        _make_path (str): A string indicating the path to store the hosts file
            in export mode.
        _trans (obj): A QtCore.QTranslator object indicating the current UI
            language setting.
        choice (list): A list containing two lists with the selection of
            functions for IPv4 and IPv6 environment.
        slices (list): A list containing two lists with integers indicating
            the number of function items from different parts listed in the
            function list.
        initd (int): An integer indicating how many times has the main dialog
            been initialized. This value would be referenced for translator
            to set the language of the main dialog.
        _mirr_id (int): An integer indicating current index number of mirrors.
        mirrors (list): A dictionary containing tag, test url, and update url
            of mirrors.
        __list_trans (list): A list containing names of function list items
            for translator to translate.
        filename (str): A string indicating the filename of the data file
            containing data to make a hosts file.
        infofile (str): A string indicating the filename of the info file
            containing metadata of the data file in JSON format.
    """
    _cur_ver = ""
    _ipv_id = 0
    _funcs = [[], []]
    _make_path = "./hosts"
    _trans = None

    choice = [[], []]
    slices = [[], []]

    initd = 0

    # Mirror related configuration
    _mirr_id = 0
    mirrors = []
    # Name of items from the function list to be localized
    __list_trans = [
        _translate("Util", "google(cn)", None),
        _translate("Util", "google(hk)", None),
        _translate("Util", "google(us)", None),
        _translate("Util", "google-apis(cn)", None),
        _translate("Util", "google-apis(us)", None),
        _translate("Util", "activation-helper", None),
        _translate("Util", "facebook", None),
        _translate("Util", "twitter", None),
        _translate("Util", "youtube", None),
        _translate("Util", "wikipedia", None),
        _translate("Util", "institutions", None),
        _translate("Util", "steam", None),
        _translate("Util", "others", None),
        _translate("Util", "adblock-hostsx", None),
        _translate("Util", "adblock-mvps", None),
        _translate("Util", "adblock-mwsl", None),
        _translate("Util", "adblock-yoyo", None), ]
    # Data file related configuration
    filename = "hostslist.data"
    infofile = "hostsinfo.json"

    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)
        super(HostsUtil, self).__init__()

    def __del__(self):
        # Clear up datafile
        try:
            RetrieveData.clear()
        except:
            pass

    def start(self):
        if not self.initd:
            self.init_main()
        self.show()
        sys.exit(self.app.exec_())

    def init_main(self):
        """Initialize the main dialog - Public Method

        Set up the elements on the main dialog. Check the environment of
        current operating system and current session.
        """
        self.Ui.SelectMirror.clear()
        # Set mirrors
        self.mirrors = CommonUtil.set_network("network.conf")
        for i, mirror in enumerate(self.mirrors):
            self.Ui.SelectMirror.addItem(_fromUtf8(""))
            self.Ui.SelectMirror.setItemText(
                i, _translate("Util", mirror["tag"], None))
            self.set_platform_label()
        # Read data file and set function list
        try:
            RetrieveData.unpack()
            RetrieveData.connect_db()
            self.set_func_list(1)
            self.refresh_func_list()
            self.set_info()
        except IOError:
            self.warning_no_datafile()
        except BadZipfile:
            self.warning_incorrect_datafile()
        # Check if current session have root privileges
        self.check_writable()
        self.initd += 1

def qt_main():
    """Load main dialog

    Start the main dialog of Hosts Setup Utility.
    """
    HostsUtlMain = HostsUtil()
    HostsUtlMain.start()

if __name__ == "__main__":
    qt_main()
