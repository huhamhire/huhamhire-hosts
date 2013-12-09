#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  curses_d.py:
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import curses
import json
import os
import shutil
import socket
import urllib
import sys

from curses_ui import CursesUI
from make import MakeHosts
from update import FetchUpdate

sys.path.append("..")
from util import CommonUtil, RetrieveData


class CursesDeamon(CursesUI):
    """
    Attributes:
        _make_cfg (dict): A dictionary containing the selection control bytes
            to make a hosts file.
        _update (dict): A dictionary containing the update information of the
            current data file on server.
        _writable (int): An integer indicating whether the program is run with
            admin/root privileges. The value could be 1 or 0.
        platform (str): A string indicating the platform of current operating
            system. The value could be "Windows", "Linux", "Unix", "OS X", and
            of course "Unkown".
        hostname (str): A string indicating the hostname of current operating
            system. This attribute would be used for linux clients.
        hostspath (str): A string indicating the absolute path of the hosts
            file on current operating system.
    """
    _make_cfg = {}
    _update = {}
    _writable = 0
    # OS related configuration
    platform = ''
    hostname = ''
    hostspath = ''

    _ops_keys = [curses.KEY_F5, curses.KEY_F6, curses.KEY_F10]
    _hot_keys = [curses.KEY_UP, curses.KEY_DOWN, 10, 32]

    def __init__(self):
        super(CursesDeamon, self).__init__()
        # Check if current session have root privileges
        self.check_writable()

    def check_writable(self):
        """Check write privileges - Public Method

        Check if current session has write privileges for the hosts file.
        """
        self._writable = CommonUtil.check_privileges()[1]
        if not self._writable:
            self.messagebox("Please check if you have writing\n"
                            "privileges to the hosts file!", 1)
            exit()

    def session_daemon(self):
        screen = self._stdscr.subwin(0, 0, 0, 0)
        screen.keypad(1)
        # Draw Menu
        self.banner()
        self.footer()
        # Key Press Operations
        key_in = None
        tab = 0
        pos = 0
        tab_entry = [self.configure_settings, self.select_func]
        while key_in != 27:
            self.setup_menu()
            self.status()
            self.process_bar(0, 0, 0, 0)
            for i, sec in enumerate(tab_entry):
                tab_entry[i](pos if i == tab else None)
            if key_in is None:
                test = self.settings[0][2][0]["test_url"]
                self.check_connection(test)
            key_in = screen.getch()
            if key_in == 9:
                if self.choice == [[], []]:
                    tab = 0
                else:
                    tab = not tab
                pos = 0
            elif key_in in self._hot_keys:
                pos = tab_entry[tab](pos, key_in)
            elif key_in in self._ops_keys:
                if key_in == curses.KEY_F10:
                    if self._funcs == [[], []]:
                        self.messagebox("No data file found! Press F6 to get "
                                        "data file first.", 1)
                    else:
                        msg = "Apply Changes to hosts file?"
                        confirm = self.messagebox(msg, 2)
                        if confirm:
                            self.set_cfgbytes()
                            maker = MakeHosts(self)
                            maker.make()
                            self.move_hosts()
                elif key_in == curses.KEY_F5:
                    self._update = self.check_update()
                elif key_in == curses.KEY_F6:
                    if self._update == {}:
                        self._update = self.check_update()
                    self.fetch_update()
                    return 1
                else:
                    pass
        return 0

    def configure_settings(self, pos=None, key_in=None):
        id_num = range(len(self.settings))
        if pos is not None:
            if key_in == curses.KEY_DOWN:
                pos = list(id_num[1:] + id_num[:1])[pos]
            elif key_in == curses.KEY_UP:
                pos = list(id_num[-1:] + id_num[:-1])[pos]
            elif key_in in [10, 32]:
                self.sub_selection(pos)
            self.info(pos, 0)
        self.configure_settings_frame(pos)
        return pos

    def select_func(self, pos=None, key_in=None):
        list_height = 15
        ip = self.settings[1][1]
        # Key Press Operations
        item_len = len(self.choice[ip])
        item_sup, item_inf = self._item_sup, self._item_inf
        if pos is not None:
            if item_len > list_height:
                if pos <= 1:
                    item_sup = 0
                    item_inf = list_height - 1
                elif pos >= item_len - 2:
                    item_sup = item_len - list_height + 1
                    item_inf = item_len
            else:
                item_sup = 0
                item_inf = item_len
            if key_in == curses.KEY_DOWN:
                pos += 1
                if pos >= item_len:
                    pos = 0
                if pos not in range(item_sup, item_inf):
                    item_sup += 2 if item_sup == 0 else 1
                    item_inf += 1
            elif key_in == curses.KEY_UP:
                pos -= 1
                if pos < 0:
                    pos = item_len - 1
                if pos not in range(item_sup, item_inf):
                    item_inf -= 2 if item_inf == item_len else 1
                    item_sup -= 1
            elif key_in in [10, 32]:
                self._funcs[ip][pos] = not self._funcs[ip][pos]
                mutex = RetrieveData.get_ids(self.choice[ip][pos][2])
                for c_id, c in enumerate(self.choice[ip]):
                    if c[0] == self.choice[ip][pos][0]:
                        if c[1] in mutex and self._funcs[ip][c_id] == 1:
                            self._funcs[ip][c_id] = 0
            self.info(pos, 1)
        else:
            item_sup = 0
            if item_len > list_height:
                item_inf = list_height - 1
            else:
                item_inf = item_len
        self.show_funclist(pos, item_sup, item_inf)
        return pos

    def sub_selection(self, pos):
        screen = self.sub_selection_dialog(pos)
        i_pos = self.settings[pos][1]
        # Key Press Operations
        id_num = range(len(self.settings[pos][2]))
        key_in = None
        while key_in != 27:
            self.sub_selection_dialog_items(pos, i_pos, screen)
            key_in = screen.getch()
            if key_in == curses.KEY_DOWN:
                i_pos = list(id_num[1:] + id_num[:1])[i_pos]
            elif key_in == curses.KEY_UP:
                i_pos = list(id_num[-1:] + id_num[:-1])[i_pos]
            elif key_in in [10, 32]:
                if pos == 0 and i_pos != self.settings[pos][1]:
                    test = self.settings[pos][2][i_pos]["test_url"]
                    self.check_connection(test)
                self.settings[pos][1] = i_pos
                return

    def check_connection(self, url):
        self.messagebox("Checking Server Status...")
        conn = CommonUtil.check_connection(url)
        if conn:
            self.statusinfo[0][1] = "OK"
            self.statusinfo[0][2] = "GREEN"
        else:
            self.statusinfo[0][1] = "Error"
            self.statusinfo[0][2] = "RED"
        self.status()
        return conn

    def check_update(self):
        self.messagebox("Checking Update...")
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
        self.messagebox("Downloading...")
        fetch_d = FetchUpdate(self)
        fetch_d.get_file()

    def set_cfgbytes(self):
        """Set configuration byte words - Public Method

        Calculate the module configuration byte words by the selection from
        function list on the main dialog.
        """
        ip_flag = self.settings[1][1]
        selection = {}
        localhost_word = {
            "Windows": 0x0001, "Linux": 0x0002,
            "Unix": 0x0002, "OS X": 0x0004}[self.platform]
        selection[0x02] = localhost_word
        ch_parts = (0x08, 0x20 if ip_flag else 0x10, 0x40)
        slices = self.slices[ip_flag]
        for i, part in enumerate(ch_parts):
            part_cfg = self._funcs[ip_flag][slices[i]:slices[i + 1]]
            part_word = 0
            for i, cfg in enumerate(part_cfg):
                part_word += cfg << i
            selection[part] = part_word
        self._make_cfg = selection

    def move_hosts(self):
        """Move hosts file to the system path after making - Public Method

        Move hosts file to the system path after making operations are
        finished.
        """
        filepath = "hosts"
        try:
            shutil.copy2(filepath, self.hostspath)
        except IOError:
            os.remove(filepath)
            return
        os.remove(filepath)
        self.messagebox("Operation completed!", 1)
