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

import os
import socket
import time

import urllib
import json

from retrievedata import RetrieveData
from utilities import Utilities

class HostsCursesUI(object):
    __stdscr = ''
    __title = "HOSTS SETUP UTILITY"
    __copyleft = "v%s Copyleft 2011-2013, Huhamhire-hosts Team" % __version__

    _writable = 0
    _make_cfg = {}
    _make_path = "./hosts"
    _sys_eol = ""
    _funcs = [[], []]
    choice = [[], []]
    slices = [[], []]

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
    update = {}

    filename = "hostslist.data"
    infofile = "hostsinfo.json"

    item_sup = 0
    item_inf = 0
    entry = None

    def __init__(self, entry=None):
        self.entry = entry
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

    def check_writable(self):
        """Check write privileges - Public Method

        Check if current session has write privileges for the hosts file.
        """
        self._writable = Utilities.check_privileges()[1]
        if not self._writable:
            self.confirm_win(3)
            exit()

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
        list_height = 15
        ip = self.settings[1][1]
        # Key Press Operations
        item_len = len(self.choice[ip])
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
        self.item_sup, self.item_inf = item_sup, item_inf
        return self.show_funclist(pos)

    def show_funclist(self, pos):
        # Set UI variable
        screen = self.__stdscr.subwin(18, 26, 2, 26)
        screen.bkgd(' ', curses.color_pair(4))
        normal = curses.A_NORMAL
        select = curses.color_pair(5)
        select += curses.A_BOLD
        list_height = 15
        # Set local variable
        ip = self.settings[1][1]
        item_len = len(self.choice[ip])
        item_sup, item_inf = self.item_sup, self.item_inf
        # Function list
        items_show = self.choice[ip][item_sup:item_inf]
        items_selec = self._funcs[ip][item_sup:item_inf]
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
            info_str = self.choice[ip][pos][3]
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
                        maker = CursesMakeHosts(self)
                        maker.make()
                elif i == 0:
                    self.update = self.check_update()
                elif i == 1:
                    if self.update == {}:
                        self.update = self.check_update()
                    self.fetch_update()
                    return
                else:
                    pass

    def set_cfgbytes(self):
        """Set configuration byte words - Public Method

        Calculate the module configuration byte words by the selection from
        function list on the main dialog.
        """
        ip_flag = self.settings[1][1]
        selection = {}
        localhost_word = {
            "Windows": 0x0001, "Linux": 0x0002,
            "Unix": 0x0002, "OS X": 0x0004}[self.platform[0]]
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
        choices = ["OK", "Cancel"]
        if op == 2:
            message = "Apply Changes to hosts file?"
        elif op == 3:
            message = "Please check your privilege!"
        # Draw subwindow frame
        screen.addstr(1, 2, message.center(36), normal)
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
            if key_in in [ord('C'), ord('O')]:
                return [ord('C'), ord('O')].index(key_in)
            if key_in in [10, 32]:
                return not tab

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
        shadow = curses.newwin(3, 30, 11, 24)
        shadow.bkgd(' ', curses.color_pair(8))
        shadow.refresh()
        # Draw Subwindow
        screen = curses.newwin(3, 30, 10, 23)
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

    def fetch_update(self):
        # Draw Shadow
        shadow = curses.newwin(3, 30, 11, 24)
        shadow.bkgd(' ', curses.color_pair(8))
        shadow.refresh()
        # Draw Subwindow
        screen = curses.newwin(3, 30, 10, 23)
        screen.box()
        screen.bkgd(' ', curses.color_pair(2))
        screen.keypad(1)

        normal = curses.A_NORMAL
        screen.addstr(1, 9, "Downloading...", normal)
        screen.refresh()

        fetch_d = CursesFetchUpdate(self)
        fetch_d.get_file()
        try:
            RetrieveData.clear()
        except Exception, e:
            pass
        self.entry.__init__()
        self.entry.opt_session()

class CursesFetchUpdate(object):
    def __init__(self, parent):
        mirror_id = parent.settings[0][1]
        mirror = parent.settings[0][2][mirror_id]
        self.url = mirror["update"] + parent.filename
        self.path = "./" + parent.filename
        self.tmp_path = self.path + ".download"
        self.filesize = parent.update["size"]
        self.parent = parent

    def get_file(self):
        socket.setdefaulttimeout(10)
        try:
            urllib.urlretrieve(self.url, self.tmp_path,
                self.parent.process_bar)
            self.replace_old()
        except Exception, e:
            raise e

    def replace_old(self):
        """Replace the old data file - Public Method

        Overwrite the old hosts data file with the new one.
        """
        if os.path.isfile(self.path):
            os.remove(self.path)
        os.rename(self.tmp_path, self.path)

class CursesMakeHosts(object):
    mod_num = 0
    make_cfg = {}
    eol = ""

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Fetch settings from the main dialog to make a new hosts file.

        Args:
            parent (obj): An instance of MainDialog object to get settings
                from.
        """
        self.make_cfg = parent._make_cfg
        make_path = parent._make_path
        self.hostname = parent.platform[1]
        self.eol = parent._sys_eol
        self.hosts_file = open("hosts", "wb")

    def make(self):
        """Make new hosts file - Public Method

        Operations to retrieve data from the data file and make the new hosts
        file for current system.
        """
        RetrieveData.connect_db()
        self.maketime = time.time()
        self.write_head()
        self.write_info()
        self.get_hosts(self.make_cfg)
        self.hosts_file.close()
        RetrieveData.disconnect_db()

    def get_hosts(self, make_cfg):
        """Make hosts by user config - Public Method

        Make the new hosts file by the configuration ({make_cfg}) from
        function list on the main dialog.

        Args:
            make_cfg (dict): A dictionary containing module settings in byte
                word format.
        """
        for part_id in sorted(make_cfg.keys()):
            mod_cfg = make_cfg[part_id]
            if not RetrieveData.chk_mutex(part_id, mod_cfg):
                return
            mods = RetrieveData.get_ids(mod_cfg)
            for mod_id in mods:
                self.mod_num += 1
                if part_id == 0x02:
                    self.write_localhost_mod(part_id, mod_id)
                else:
                    self.write_common_mod(part_id, mod_id)

    def write_head(self):
        """Write head section - Public Method

        Write the head part of new hosts file.
        """
        for head_str in RetrieveData.get_head():
            self.hosts_file.write("%s%s" % (head_str[0], self.eol))

    def write_info(self):
        """Write info section - Public Method

        Write the information part of new hosts file.
        """
        info = RetrieveData.get_info()
        info_lines = ["#"]
        info_lines.append("# %s: %s" % ("Version", info["Version"]))
        info_lines.append("# %s: %s" % ("Buildtime", info["Buildtime"]))
        info_lines.append("# %s: %s" % ("Applytime", int(self.maketime)))
        info_lines.append("#")
        for line in info_lines:
            self.hosts_file.write("%s%s" % (line, self.eol))

    def write_common_mod(self, part_id, mod_id):
        """Write module section - Public Method

        Write hosts entries in a specified module ({mod_id}) from a specified
        part ({part_id}) of the data file to the new hosts file.

        Args:
            part_id (int): An integer indicating the index number of a part
                in the data file.
            mod_id (int): An integer indicating the index number of a module
                in the data file.
        """
        hosts, mod_name = RetrieveData.get_host(part_id, mod_id)
        self.hosts_file.write(
            "%s# Section Start: %s%s" % (self.eol, mod_name, self.eol))
        for host in hosts:
            self.hosts_file.write("%s %s%s" % (host[0], host[1], self.eol))
        self.hosts_file.write("# Section End: %s%s" % (mod_name, self.eol))

    def write_localhost_mod(self, part_id, mod_id):
        """Write localhost section - Public Method

        Write hosts entries in a localhost module ({mod_id}) from a specified
        part ({part_id}) of the data file to the new hosts file.

        Args:
            part_id (int): An integer indicating the index number of a part
                in the data file.
            mod_id (int): An integer indicating the index number of a module
                in the data file.
        """
        hosts, mod_name = RetrieveData.get_host(part_id, mod_id)
        self.hosts_file.write(
            "%s# Section Start: Localhost%s" % (self.eol, self.eol))
        for host in hosts:
            if "#Replace" in host[1]:
                host = (host[0], self.hostname)
            self.hosts_file.write("%s %s%s" % (host[0], host[1], self.eol))
        self.hosts_file.write("# Section End: Localhost%s" % (self.eol))
