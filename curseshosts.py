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

__version__ = '1.9.7'
__revision__ = "$Id$"
__author__ = "huhamhire <me@huhamhire.com>"

__all__ = [ 'HostsCurses' ]

from curseshostsui import HostsCursesUI
from retrievedata import RetrieveData, make_hosts
from utilities import Utilities

from zipfile import BadZipfile

class HostsCurses(object):
    _ipv_id = 0
    _writable = 0
    _down_flag = 0
    _funcs = [[], []]
    _hostsinfo = []
    _make_cfg = {}
    _make_mode = ""
    _make_path = "./hosts"
    _sys_eol = ""
    _update = {}
    hostsinfo = ["N/A", "N/A"]

    choice = [[], []]
    slices = [[], []]
    # OS related configuration
    platform = ''
    hostname = ''
    hostspath = ''
    # Mirror related configuration
    _mirr_id = 0
    mirrors = []
    # Data file related configuration
    filename = "hostslist.data"
    infofile = "hostsinfo.json"

    def __init__(self):
        # Set mirrors
        self.mirrors = Utilities.set_network("network.conf")
        self.set_platform()
        # Read data file and set function list
        try:
            RetrieveData.unpack()
            RetrieveData.connect_db()
            self.set_func_list()
            self.set_info()
        except IOError:
            pass
        except BadZipfile:
            pass
        # Check if current session have root privileges
        self.check_writable()

    def opt_session(self):
        window = HostsCursesUI()
        window.func_items = self.choice
        window.func_selec = self._funcs
        window.hostsinfo["Version"] = self.hostsinfo[0]
        window.hostsinfo["Release"] = self.hostsinfo[1]
        window.settings[0][2] = self.mirrors

        window.section_daemon()

        # Clear up datafile
        try:
            RetrieveData.clear()
        except:
            pass

    def set_platform(self):
        """Set OS info - Public Method

        Set the information of current operating system platform.
        """
        system, hostname, path, encode, flag = Utilities.check_platform()
        color = "GREEN" if flag else "RED"
        self.platform = system
        self.hostname = hostname
        self.hostspath = path
        if encode == "win_ansi":
            self._sys_eol = "\r\n"
        else:
            self._sys_eol = "\n"

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
        ver = info["Version"]
        build = info["Buildtime"]
        build = Utilities.timestamp_to_date(build)
        self.hostsinfo = [ver, build]

    def check_writable(self):
        """Check write privileges - Public Method

        Check if current session has write privileges for the hosts file.
        """
        writable = Utilities.check_privileges()[1]
        self._writable = writable
        if not writable:
            #self.warning_permission()
            pass


class HostsDownload(object):
    def get_file(self, url, path, ui_class):
        socket.setdefaulttimeout(10)
        urllib.urlretrieve(url, path, ui_class.process_bar)


if __name__ == "__main__":
    main = HostsCurses()
    main.opt_session()
