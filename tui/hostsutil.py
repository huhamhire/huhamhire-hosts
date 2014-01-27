#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hostsutil.py: Start a TUI session of `Hosts Setup Utility`.
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import os

from zipfile import BadZipfile

from curses_d import CursesDaemon

import sys
sys.path.append("..")
from util import CommonUtil, RetrieveData


class HostsUtil(CursesDaemon):
    """
    HostsUtil class in :mod:`tui` module is the main entrance to the
    Text-based User Interface (TUI) mode of `Hosts Setup Utility`. This class
    contains methods to start a TUI session of `Hosts Setup Utility`.

    .. note:: This class is subclass of :class:`~tui.curses_d.CursesDaemon`
        class.

    .. inheritance-diagram:: tui.hostsutil.HostsUtil
        :parts: 2

    Typical usage to start a TUI session::

        import tui

        util = tui.HostsUtil()
        util.start()

    :ivar str platform: Platform of current operating system. The value could
        be `Windows`, `Linux`, `Unix`, `OS X`, and of course `Unknown`.
    :ivar str hostname: The hostname of current operating system.

        .. note:: This attribute would only be used on linux.
    :ivar str hosts_path: The absolute path to the hosts file on current
        operating system.

        .. seealso:: :attr:`platform`, :attr:`hostname`, :attr:`hosts_path` in
            :class:`~tui.curses_d.CursesDaemon` class.
    :ivar str sys_eol: The End-Of-Line marker. This maker could typically be
        one of `CR`, `LF`, or `CRLF`.

        .. seealso:: :attr:`sys_eol` in :class:`~tui.curses_ui.CursesUI`
            class.
    """
    platform = ""
    hostname = ""
    hosts_path = ""
    sys_eol = ""

    def __init__(self):
        """
        Initialize a new TUI session.

        * Load server list from a configuration file under working directory.
        * Try to load the hosts data file under working directory if it
          exists.

        .. note:: IF hosts data file does not exists correctly in current
            working directory, a warning message box would popup. And
            operations to change the hosts file on current system could be
            done only until a new data file has been downloaded.

        .. seealso:: :meth:`~tui.curses_d.CursesDaemon.session_daemon` method
            in :class:`~tui.curses_d.CursesDaemon`.

        .. seealso:: :meth:`~gui.hostsutil.HostsUtil.init_main` in
            :class:`~gui.hostsutil.HostsUtil` class.
        """
        super(HostsUtil, self).__init__()
        # Set mirrors
        self.settings[0][2] = CommonUtil.set_network("network.conf")
        # Read data file and set function list
        try:
            self.set_platform()
            RetrieveData.unpack()
            RetrieveData.connect_db()
            self.set_info()
            self.set_func_list()
        except IOError:
            self.messagebox("No data file found! Press F6 to get data file "
                            "first.", 1)
        except BadZipfile:
            self.messagebox("Incorrect Data file! Press F6 to get a new data "
                            "file first.", 1)

    def __del__(self):
        """
        Reset the terminal and clear up the temporary data file while TUI
        session is finished.
        """
        super(HostsUtil, self).__del__()
        try:
            RetrieveData.clear()
        except:
            pass

    def start(self):
        """
        Start the TUI session.

        .. note:: This method is the trigger to start a TUI session of
            `Hosts Setup Utility`.
        """
        while True:
            # Reload
            if self.session_daemon():
                self.__del__()
                self.__init__()
            else:
                break

    def set_platform(self):
        """
        Set the information about current operating system.
        """
        system, hostname, path, encode, flag = CommonUtil.check_platform()
        color = "GREEN" if flag else "RED"
        self.platform = system
        self.statusinfo[1][1] = system
        self.hostname = hostname
        self.hosts_path = path
        self.statusinfo[1][2] = color
        if encode == "win_ansi":
            self.sys_eol = "\r\n"
        else:
            self.sys_eol = "\n"

    def set_func_list(self):
        """
        Set the function selection list in TUI session.
        """
        for ip in range(2):
            choice, defaults, slices = RetrieveData.get_choice(ip)
            if os.path.isfile(self.custom):
                choice.insert(0, [4, 1, 0, "customize"])
                defaults[0x04] = [1]
                for i in range(len(slices)):
                    slices[i] += 1
                slices.insert(0, 0)
            self.choice[ip] = choice
            self.slices[ip] = slices
            funcs = []
            for func in choice:
                if func[1] in defaults[func[0]]:
                    funcs.append(1)
                else:
                    funcs.append(0)
            self._funcs[ip] = funcs

    def set_info(self):
        """
        Set the information of the current local data file.
        """
        info = RetrieveData.get_info()
        build = info["Buildtime"]
        self.hostsinfo["Version"] = info["Version"]
        self.hostsinfo["Release"] = CommonUtil.timestamp_to_date(build)

if __name__ == "__main__":
    main = HostsUtil()
    main.start()
