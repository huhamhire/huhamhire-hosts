#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hostsutil.py : Main parts of Hosts Setup Utility
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

__version__ = "1.9.8"
__revision__ = "$Id$"
__author__ = "huhamhire <me@huhamhire.com>"

import sys

from PyQt4 import QtGui
from zipfile import BadZipfile

from qdialog_slots import QDialogSlots

sys.path.append("..")
from util import RetrieveData, CommonUtil

# Path to store language files
LANG_DIR = "./gui/lang/"


class HostsUtil(QDialogSlots):
    """A class to manage the operations and UI of Hosts Setup Utility

    HostsUtil class is a subclass of PyQt4.QtGui.QDialog which is used to
    make the main dialog of this hosts setup utility.
    This class contains a set of tools used to manage the operations while
    modifying the hosts file of current operating system. Including methods
    to manage operations to update data file, download data file, configure
    hosts, make hosts file, backup hosts file, and restore backup.
    The HostsUtil class also provides QT slots to deal with the QT singles
    emitted by the widgets on the main dialog operated by users. Extend
    methods dealing with the user interface is also given by this class.

    Attributes:
        init_flag (int): An integer indicating how many times has the main
            dialog been initialized. This value would be referenced for
            translator to set the language of the main dialog.
        filename (str): A string indicating the filename of the data file
            containing data to make a hosts file.
        infofile (str): A string indicating the filename of the info file
            containing metadata of the data file in JSON format.
    """
    init_flag = 0
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
        if not self.init_flag:
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
        self.set_mirrors()
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
        self.init_flag += 1


if __name__ == "__main__":
    HostsUtlMain = HostsUtil()
    HostsUtlMain.start()
