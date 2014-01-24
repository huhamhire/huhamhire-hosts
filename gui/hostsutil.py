#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hostsutil.py : Main entrance to GUI module of Hosts Setup Utility.
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

import sys

from zipfile import BadZipfile

from qdialog_slots import QDialogSlots

sys.path.append("..")
from util import RetrieveData, CommonUtil

# Path to store language files
LANG_DIR = "./gui/lang/"


class HostsUtil(QDialogSlots):
    """
    HostsUtil class is the main entrance to the Graphical User Interface (GUI)
    module of `Hosts Setup Utility`. This class contains methods to launch the
    main dialog of this utility.

    .. note:: This class is subclass of
        :class:`~gui.qdialog_slots.QDialogSlots` class.

    Typical usage to start a GUI session::

        import gui

        util = gui.HostsUtil()
        util.start()

    :ivar int init_flag: Times of the main dialog being initialized. This
        value would be referenced for translator to set the language of the
        main dialog.
    :ivar str filename: Filename of the hosts data file containing data to
        make hosts files from. Default by "`hostslist.data`".
    :ivar str infofile: Filename of the info file containing metadata of the
        hosts data file formatted in JSON. Default by "`hostslist.json`".

    .. seealso:: :attr:`filename` and :attr:`infofile` in
        :class:`~tui.curses_ui.CursesUI` class.
    """
    init_flag = 0
    # Data file related configuration
    filename = "hostslist.data"
    infofile = "hostsinfo.json"

    def __init__(self):
        super(HostsUtil, self).__init__()

    def __del__(self):
        """
        Clear up the temporary data file while TUI session is finished.
        """
        try:
            RetrieveData.clear()
        except:
            pass

    def start(self):
        """
        Start the GUI session.

        .. note:: This method is the trigger to launch a GUI session of
            `Hosts Setup Utility`.
        """
        if not self.init_flag:
            self.init_main()
        self.show()
        sys.exit(self.app.exec_())

    def init_main(self):
        """
        Set up the elements on the main dialog. Check the environment of
        current operating system and current session.

        * Load server list from a configuration file under working directory.
        * Try to load the hosts data file under working directory if it
          exists.

        .. note:: IF hosts data file does not exists correctly in current
            working directory, a warning message box would popup. And
            operations to change the hosts file on current system could be
            done only until a new data file has been downloaded.

        .. seealso:: Method :meth:`~tui.hostsutil.HostsUtil.__init__` in
            :class:`~tui.hostsutil.HostsUtil` class.
        """
        self.ui.SelectMirror.clear()
        self.set_version()
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
