#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hcurses.py:
#
# Copyleft (C) 2013 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

from zipfile import BadZipfile

from curses_d import CursesDeamon
from retrievedata import RetrieveData
from utilities import Utilities

class HostsUtil(CursesDeamon):
    _down_flag = 0
    _hostsinfo = []
    _update = {}

    def __init__(self):
        super(HostsUtil, self).__init__()
        # Set mirrors
        self.settings[0][2] = Utilities.set_network("network.conf")
        # Read data file and set function list
        try:
            RetrieveData.unpack()
            RetrieveData.connect_db()
            self.set_platform()
            self.set_func_list()
            self.set_info()
        except IOError:
            pass
        except BadZipfile:
            pass

    def set_platform(self):
        """Set OS info - Public Method

        Set the information of current operating system platform.
        """
        system, hostname, path, encode, flag = Utilities.check_platform()
        color = "GREEN" if flag else "RED"
        self.platform = system
        self.statusinfo[1][1] = system
        self.hostname = hostname
        self.hostspath = path
        self.statusinfo[1][2] = color
        if encode == "win_ansi":
            self._sys_eol = "\r\n"
        else:
            self._sys_eol = "\n"

    def startutil(self):
        self.session_daemon()
        # Clear up datafile
        try:
            RetrieveData.clear()
        except:
            pass

    def set_func_list(self):
        for ip in range(2):
            choice, defaults, slices = RetrieveData.get_choice(ip)
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
        """Set data file info - Public Method

        Set the information of the current local data file.
        """
        info = RetrieveData.get_info()
        build = info["Buildtime"]
        self.hostsinfo["Version"] = info["Version"]
        self.hostsinfo["Release"] = Utilities.timestamp_to_date(build)

if __name__ == "__main__":
    main = HostsUtil()
    main.startutil()
