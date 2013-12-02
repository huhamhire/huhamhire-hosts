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

__all__ = [ 'HostsCursesUI' ]

import curses
import locale

import os, sys
import socket

import math
import urllib
import json

from zipfile import BadZipfile

from retrievedata import RetrieveData, make_hosts
from utilities import Utilities

class HostsCursesUI(object):
    __stdscr = ''
    __title = "HOSTS SETUP UTILITY"
    __copyleft = "v%s Copyleft 2011-2013, Huhamhire-hosts Team" % __version__

    colorpairs = [(curses.COLOR_WHITE, curses.COLOR_BLUE),
                  (curses.COLOR_WHITE, curses.COLOR_RED),
                  (curses.COLOR_YELLOW, curses.COLOR_BLUE),
                  (curses.COLOR_BLUE, curses.COLOR_WHITE),
                  (curses.COLOR_WHITE, curses.COLOR_WHITE),
                  (curses.COLOR_BLACK, curses.COLOR_WHITE),
                  (curses.COLOR_GREEN, curses.COLOR_WHITE),
                  (curses.COLOR_WHITE, curses.COLOR_BLACK),
                  (curses.COLOR_RED, curses.COLOR_WHITE),]
    ops_keys = [curses.KEY_F5, curses.KEY_F6, curses.KEY_F10]
    hotkeys = [curses.KEY_UP, curses.KEY_DOWN, 10, 32]
    func_items = [[], []]
    func_selec = [[], []]
    settings = [["Server", 0, []],
                ["IP Version", 0, ["IPv4", "IPv6"]]]
    funckeys = [["", "Select Item"], ["Tab", "Select Field"],
                ["Enter", "Set Item"], ["F5", "Check Update"],
                ["F6", "Get Update"], ["F10", "Apply Changes"],
                ["Esc", "Exit"]]
    subtitles = [["Configure Settings", (1, 2)], ["Status", (8, 2)],
                 ["Hosts File", (13, 2)], ["Select Functions", (1, 28)]]
    statusinfo = [["Connection", "N/A", "GREEN"], ["OS", "N/A", "GREEN"]]
    hostsinfo = {"Version": "N/A", "Release": "N/A", "Latest": "N/A"}
    platform = []

    filename = "hostslist.data"
    infofile = "hostsinfo.json"

    item_sup = 0
    item_inf = 0

    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.__stdscr = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        # Set colors
        curses.use_default_colors()
        for i, color in enumerate(self.colorpairs):
            curses.init_pair(i + 1, *color)

    def banner(self):
        screen = self.__stdscr.subwin(2, 80, 0, 0)
        screen.bkgd(' ', curses.color_pair(1))
        # Set local variable
        title = curses.A_NORMAL
        title += curses.A_BOLD
        normal = curses.color_pair(4)
        # Print title
        screen.addstr(0, 0, self.__title.center(79), title)
        screen.addstr(1, 0, "Setup".center(10), normal)
        screen.refresh()

    def footer(self):
        screen = self.__stdscr.subwin(1, 80, 23, 0)
        screen.bkgd(' ', curses.color_pair(1))
        # Set local variable
        normal = curses.A_NORMAL
        # Copyright info
        copyleft = self.__copyleft
        screen.addstr(0, 0, copyleft.center(79), normal)
        screen.refresh()

    def configure_settings(self, pos=None, key_in=None):
        self.__stdscr.keypad(1)
        screen = self.__stdscr.subwin(8, 25, 2, 0)
        screen.bkgd(' ', curses.color_pair(4))
        # Set local variable
        normal = curses.A_NORMAL
        select = curses.color_pair(5)
        select += curses.A_BOLD

        id_num = range(len(self.settings))
        if pos != None:
            if key_in == curses.KEY_DOWN:
                pos = list(id_num[1:] + id_num[:1])[pos]
            elif key_in == curses.KEY_UP:
                pos = list(id_num[-1:] + id_num[:-1])[pos]
            elif key_in in [10, 32]:
                self.sub_selection(pos)
            self.info(pos, 0)
        for p, item in enumerate(self.settings):
            item_str = item[0].ljust(12)
            screen.addstr(3 + p, 2, item_str, select if p == pos else normal)
            if p:
                choice = "[%s]" % item[2][item[1]]
            else:
                choice = "[%s]" % item[2][item[1]]["label"]
            screen.addstr(3 + p, 15, ''.ljust(10), normal)
            screen.addstr(3 + p, 15, choice, select if p == pos else normal)
        screen.refresh()
        return pos

    def status(self):
        screen = self.__stdscr.subwin(11, 25, 10, 0)
        screen.bkgd(' ', curses.color_pair(4))
        # Set local variable
        normal = curses.A_NORMAL
        green = curses.color_pair(7)
        red = curses.color_pair(9)
        # Status info
        for i, stat in enumerate(self.statusinfo):
            screen.addstr(2 + i, 2, stat[0], normal)
            stat_str = ''.join(['[', stat[1], ']']).ljust(9)
            screen.addstr(2 + i, 15, stat_str,
                green if stat[2] == "GREEN" else red)
        # Hosts file info
        i = 0
        for key, info in self.hostsinfo.items():
            screen.addstr(7 + i, 2, key, normal)
            screen.addstr(7 + i, 15, info, normal)
            i += 1
        screen.refresh()

    def select_func(self, pos=None, key_in=None):
        screen = self.__stdscr.subwin(18, 26, 2, 26)
        screen.bkgd(' ', curses.color_pair(4))
        # Set local variable
        normal = curses.A_NORMAL
        select = curses.color_pair(5)
        select += curses.A_BOLD
        list_height = 15
        ip = self.settings[1][1]
        # Key Press Operations
        item_len = len(self.func_items[ip])
        item_sup, item_inf = self.item_sup, self.item_inf
        if pos != None:
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
                self.func_selec[ip][pos] = not self.func_selec[ip][pos]
                mutex = RetrieveData.get_ids(self.func_items[ip][pos][2])
                for c_id, c in enumerate(self.func_items[ip]):
                    if c[0] == self.func_items[ip][pos][0]:
                        if c[1] in mutex and self.func_selec[ip][c_id] == 1:
                            self.func_selec[ip][c_id] = 0
            self.info(pos, 1)
        else:
            item_sup = 0
            if item_len > list_height:
                item_inf = list_height - 1
            else:
                item_inf = item_len
        # Function list
        items_show = self.func_items[ip][item_sup:item_inf]
        items_selec = self.func_selec[ip][item_sup:item_inf]
        for p, item in enumerate(items_show):
            sel_ch = '+' if items_selec[p] else ' '
            item_str = ("[%s] %s" % (sel_ch, item[3])).ljust(23)
            item_pos = pos - item_sup if pos != None else None
            highlight = select if p == item_pos else normal
            if item_len > list_height:
                if item_inf - item_sup == list_height - 2:
                    screen.addstr(4 + p, 2, item_str, highlight)
                elif item_inf == item_len:
                    screen.addstr(4 + p, 2, item_str, highlight)
                elif item_sup == 0:
                    screen.addstr(3 + p, 2, item_str, highlight)
            else:
                screen.addstr(3 + p, 2, item_str, highlight)
        if item_len > list_height:
            if item_inf - item_sup == list_height - 2:
                screen.addstr(3, 2, " More  ".center(23, '.'), normal)
                screen.addch(3, 15, curses.ACS_UARROW)
                screen.addstr(17, 2, " More  ".center(23, '.'), normal)
                screen.addch(17, 15, curses.ACS_DARROW)
            elif item_inf == item_len:
                screen.addstr(3, 2, " More  ".center(23, '.'), normal)
                screen.addch(3, 15, curses.ACS_UARROW)
            elif item_sup == 0:
                screen.addstr(17, 2, " More  ".center(23, '.'), normal)
                screen.addch(17, 15, curses.ACS_DARROW)
        else:
            for line_i in range(list_height - item_len):
                screen.addstr(17 - line_i, 2, ' ' * 23, normal)
        screen.refresh()

        self.item_sup, self.item_inf = item_sup, item_inf
        return pos

    def info(self, pos, tab):
        screen = self.__stdscr.subwin(18, 24, 2, 52)
        screen.bkgd(' ', curses.color_pair(4))
        normal = curses.A_NORMAL
        if tab:
            ip = self.settings[1][1]
            info_str = self.func_items[ip][pos][3]
        else:
            info_str = self.settings[pos][0]
        # Clear Expired Infomotion
        for i in range(6):
            screen.addstr(1 + i, 2, ''.ljust(22), normal)
        screen.addstr(1, 2, info_str, normal)
        # Key Info Offset
        k_info_y = 10
        k_info_x_key = 2
        k_info_x_text = 10
        # Arrow Keys
        screen.addch(k_info_y, k_info_x_key, curses.ACS_UARROW, normal)
        screen.addch(k_info_y, k_info_x_key + 1, curses.ACS_DARROW, normal)
        # Show Key Info
        for i, keyinfo in enumerate(self.funckeys):
            screen.addstr(k_info_y + i, k_info_x_key, keyinfo[0], normal)
            screen.addstr(k_info_y + i, k_info_x_text, keyinfo[1], normal)
        screen.refresh()

    def process_bar(self, done, block, total, mode=1):
        screen = self.__stdscr.subwin(2, 80, 20, 0)
        screen.bkgd(' ', curses.color_pair(4))
        normal = curses.A_NORMAL
        line_width = 76
        prog_len = line_width - 20
        # Progress Bar
        if mode:
            done = done * block
            prog = prog_len * done / total
            progress = ''.join(['=' * int(prog), '-' * int(2 * prog % 2)])
            progress = progress.ljust(prog_len)
            total = Utilities.convert_size(total).ljust(7)
            done = Utilities.convert_size(done).rjust(7)
        else:
            progress = ' ' * prog_len
            done = total = 'N/A'.center(7)
        # Show Progress
        prog_bar = "[%s] %s | %s" % (progress, done, total)
        screen.addstr(1, 2, prog_bar, normal)
        screen.refresh()

    def section_daemon(self):
        screen = self.__stdscr.subwin(0, 0, 0, 0)
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
                if self.func_items == [[], []]:
                    tab = 0
                else:
                    tab = not tab
                pos = 0
            elif key_in in hot_keys:
                pos = tab_entry[tab](pos, key_in)
            elif key_in in self.ops_keys:
                i = self.ops_keys.index(key_in)
                if i:
                    confirm = self.confirm_win(i)
                else:
                    self.check_update()

    def sub_selection(self, pos):
        i_len = len(self.settings[pos][2])
        i_pos = self.settings[pos][1]
        # Draw Shadow
        shadow = curses.newwin(i_len + 2, 18, 13 - i_len / 2, 31)
        shadow.bkgd(' ', curses.color_pair(8))
        shadow.refresh()
        # Draw Subwindow
        screen = curses.newwin(i_len + 2, 18, 12 - i_len / 2, 30)
        screen.box()
        screen.bkgd(' ', curses.color_pair(1))
        screen.keypad(1)
        # Set local variable
        normal = curses.A_NORMAL
        select = normal + curses.A_BOLD
        # Title of Subwindow
        screen.addstr(0, 3, self.settings[pos][0].center(12), normal)
        # Key Press Operations
        id_num = range(len(self.settings[pos][2]))
        key_in = None
        while key_in != 27:
            for p, item in enumerate(self.settings[pos][2]):
                item_str = item if pos else item["tag"]
                screen.addstr(1 + p, 2, item_str,
                    select if p == i_pos else normal)
            screen.refresh()
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

    def setup_menu(self):
        screen = self.__stdscr.subwin(21, 80, 2, 0)
        screen.box()
        screen.bkgd(' ', curses.color_pair(4))
        # Configuration Section
        screen.addch(0, 26, curses.ACS_BSSS)
        screen.vline(1, 26, curses.ACS_VLINE, 17)
        # Status Section
        screen.addch(7, 0, curses.ACS_SSSB)
        screen.addch(7, 26, curses.ACS_SBSS)
        screen.hline(7, 1, curses.ACS_HLINE, 25)
        # Select Functions Section
        screen.addch(0, 52, curses.ACS_BSSS)
        screen.vline(1, 52, curses.ACS_VLINE, 17)
        # Process Bar Section
        screen.addch(18, 0, curses.ACS_SSSB)
        screen.addch(18, 79, curses.ACS_SBSS)
        screen.hline(18, 1, curses.ACS_HLINE, 78)
        screen.addch(18, 26, curses.ACS_SSBS)
        screen.addch(18, 52, curses.ACS_SSBS)
        # Section Titles
        title = curses.color_pair(6)
        for s_title in self.subtitles:
            cord = s_title[1]
            screen.addstr(cord[0], cord[1], s_title[0], title)
            screen.hline(cord[0] + 1, cord[1], curses.ACS_HLINE, 23)
        screen.refresh()

    def confirm_win(self, op):
        # Draw Shadow
        shadow = curses.newwin(5, 40, 11, 21)
        shadow.bkgd(' ', curses.color_pair(8))
        shadow.refresh()
        # Draw Subwindow
        screen = curses.newwin(5, 40, 10, 20)
        screen.box()
        screen.bkgd(' ', curses.color_pair(2))
        screen.keypad(1)
        # Set local variable
        normal = curses.A_NORMAL
        select = curses.A_REVERSE
        messages = ["Apply Changes to hosts file?",
                    "Backup current hosts file?",
                    "Restore hosts from a backup?"]
        choices = ["Apply", "Cancel"]
        # Draw subwindow frame
        screen.addstr(1, 2, messages[op].center(36), normal)
        screen.hline(2, 1, curses.ACS_HLINE, 38)
        screen.addch(2, 0, curses.ACS_SSSB)
        screen.addch(2, 39, curses.ACS_SBSS)
        # Apply or Cancel the Operation
        tab = 0
        key_in = None
        while key_in != 27:
            for i, item in enumerate(choices):
                item_str = ''.join(['[', item, ']'])
                screen.addstr(3, 6 + 20 * i, item_str,
                    select if i == tab else normal)
            screen.refresh()
            key_in = screen.getch()
            if key_in in [9, curses.KEY_LEFT, curses.KEY_RIGHT]:
                tab = [1, 0][tab]
            if key_in in [ord('a'), ord('c')]:
                key_in -= (ord('a') - ord('A'))
            if key_in in [ord('A'), ord('C')]:
                return [ord('A'), ord('C')].index(key_in)
            if key_in in [10, 32]:
                return tab

    def check_connection(self, url):
        # Draw Shadow
        shadow = curses.newwin(3, 30, 11, 21)
        shadow.bkgd(' ', curses.color_pair(8))
        shadow.refresh()
        # Draw Subwindow
        screen = curses.newwin(3, 30, 10, 20)
        screen.box()
        screen.bkgd(' ', curses.color_pair(2))
        screen.keypad(1)

        normal = curses.A_NORMAL
        screen.addstr(1, 3, "Checking Server Status...", normal)
        screen.refresh()

        conn = Utilities.check_connection(url)
        if conn:
            self.statusinfo[0][1] = "OK"
            self.statusinfo[0][2] = "GREEN"
        else:
            self.statusinfo[0][1] = "Error"
            self.statusinfo[0][2] = "RED"
        self.status()
        return conn

    def check_platform(self):
        plat = Utilities.check_platform()
        self.statusinfo[1] = [self.statusinfo[1][0], plat[0],
            "GREEN" if plat[4] else "RED"]
        self.status()
        return plat

    def check_update(self):
        # Draw Shadow
        shadow = curses.newwin(3, 30, 11, 21)
        shadow.bkgd(' ', curses.color_pair(8))
        shadow.refresh()
        # Draw Subwindow
        screen = curses.newwin(3, 30, 10, 20)
        screen.box()
        screen.bkgd(' ', curses.color_pair(2))
        screen.keypad(1)

        normal = curses.A_NORMAL
        screen.addstr(1, 7, "Checking Update...", normal)
        screen.refresh()

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

class HostsCurses(object):
    _ipv_id = 0
    _is_root = 0
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

    def init_main(self):
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
        self.check_root()

    def opt_session(self):
        window = HostsCursesUI()
        window.func_items = self.choice
        window.func_selec = self._funcs
        window.hostsinfo["Version"] = self.hostsinfo[0]
        window.hostsinfo["Release"] = self.hostsinfo[1]
        window.settings[0][2] = self.mirrors

        window.section_daemon()

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

    def check_root(self):
        """Check root privileges - Public Method

        Check if current session is ran with root privileges.
        """
        is_root = Utilities.check_privileges()[1]
        self._is_root = is_root
        if not is_root:
            #self.warning_permission()
            pass


class HostsDownload(object):
    def get_file(self, url, path, ui_class):
        socket.setdefaulttimeout(10)
        urllib.urlretrieve(url, path, ui_class.process_bar)

if __name__ == "__main__":
    main = HostsCurses()
    main.init_main()
    main.opt_session()
