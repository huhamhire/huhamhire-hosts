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

__all__ = [ 'CursesDeamon' ]

import json
import socket
import sys
import urllib

from curses_ui import CursesUI
from fetchupdate import FetchUpdate
from makehosts import MakeHosts

sys.path.append("..")
from retrievedata import RetrieveData
from utilities import Utilities

class CursesDeamon(CursesUI):
    def __init__(self, entry=None):
        super(CursesDeamon, self).__init__(entry)

    def check_writable(self):
        """Check write privileges - Public Method

        Check if current session has write privileges for the hosts file.
        """
        self._writable = Utilities.check_privileges()[1]
        if not self._writable:
            self.confirm_win(3)
            exit()

    def section_daemon(self):
        screen = self._stdscr.subwin(0, 0, 0, 0)
        # Check if current session have root privileges
        self.check_writable()
        screen.keypad(1)
        # Draw Menu
        self.banner()
        self.footer()
        # Key Press Operations
        key_in = None
        tab = 0
        pos = 0
        hot_keys = self.hotkeys
        tab_entry = [self.configure_settings, self.select_func]
        while key_in != 27:
            self.setup_menu()
            self.status()
            self.process_bar(0, 0, 0, 0)
            for i, sec in enumerate(tab_entry):
                tab_entry[i](pos if i == tab else None)
            if key_in == None:
                self.platform = self.check_platform()
                test = self.settings[0][2][0]["test_url"]
                self.check_connection(test)
            key_in = screen.getch()
            if key_in == 9:
                if self.choice == [[], []]:
                    tab = 0
                else:
                    tab = not tab
                pos = 0
            elif key_in in hot_keys:
                pos = tab_entry[tab](pos, key_in)
            elif key_in in self.ops_keys:
                i = self.ops_keys.index(key_in)
                if i > 1:
                    confirm = self.confirm_win(i)
                    if confirm:
                        self.set_cfgbytes()
                        maker = MakeHosts(self)
                        maker.make()
                        self.move_hosts()
                elif i == 0:
                    self.update = self.check_update()
                elif i == 1:
                    if self.update == {}:
                        self.update = self.check_update()
                    self.fetch_update()
                    return
                else:
                    pass

    def check_platform(self):
        plat = Utilities.check_platform()
        self.statusinfo[1] = [self.statusinfo[1][0], plat[0],
            "GREEN" if plat[4] else "RED"]
        self.status()
        return plat

    def check_connection(self, url):
        self.operation_message("Checking Server Status...")
        conn = Utilities.check_connection(url)
        if conn:
            self.statusinfo[0][1] = "OK"
            self.statusinfo[0][2] = "GREEN"
        else:
            self.statusinfo[0][1] = "Error"
            self.statusinfo[0][2] = "RED"
        self.status()
        return conn

    def check_update(self):
        self.operation_message("Checking Update...")
        srv_id = self.settings[0][1]
        url = self.settings[0][2][srv_id]["update"] + self.infofile
        try:
            socket.setdefaulttimeout(5)
            urlobj = urllib.urlopen(url)
            j_str = urlobj.read()
            urlobj.close()
            info = json.loads(j_str)
        except:
            info = {"version": "[Error]"}
        self.hostsinfo["Latest"] = info["version"]
        self.status()
        return info

    def fetch_update(self):
        self.operation_message("Downloading...")
        fetch_d = FetchUpdate(self)
        fetch_d.get_file()
        try:
            RetrieveData.clear()
        except Exception, e:
            pass
        self.entry.__init__()
        self.entry.opt_session()