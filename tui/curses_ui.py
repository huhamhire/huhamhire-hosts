#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  curses_ui.py: Draw TUI using curses.
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import curses
import locale

import sys
sys.path.append("..")
from util import CommonUtil
from __version__ import __version__, __release__


class CursesUI(object):
    """
    CursesUI class contains methods to draw the Text-based User Interface
    (TUI) of Hosts Setup Utility. The methods to make TUI here are based on
    `curses <http://docs.python.org/2/library/curses.html>`_.

    :ivar str __title: Title of the TUI utility.
    :ivar str __copyleft: Copyleft information of the TUI utility.
    :ivar WindowObject _stdscr: A **WindowObject** which represents the whole
        screen.
    :ivar int _item_sup: Upper bound of item index from `function selection
        list`.
    :ivar int _item_inf: Lower bound of item index from `function selection
        list`.
    :ivar str _make_path: Temporary path to store the hosts file in while
        building. The default _make_path is `./hosts`.
    :ivar list _funcs: Two lists with the information of function list both
        for IPv4 and IPv6 environment.
    :ivar list choice: Two lists with the selection of functions both
        for IPv4 and IPv6 environment.
    :ivar list slices: Two lists with integers indicating the number of
        function items from different parts listed in the function list.

        .. seealso:: `_funcs`, `choice`, and `slices` in
            :class:`~gui.qdialog_d.QDialogDaemon` class.

    :ivar str sys_eol: The End-Of-Line marker. This maker could typically be
        one of `CR`, `LF`, or `CRLF`.

        .. seealso:: :attr:`sys_eol` in
            :class:`~gui.qdialog_d.QDialogDaemon` class.

    :ivar list colorpairs: Tuples of `(foreground-color, background-color)`
        used while drawing TUI.

        The default colorpairs is defined as::

            colorpairs = [(curses.COLOR_WHITE, curses.COLOR_BLUE),
                          (curses.COLOR_WHITE, curses.COLOR_RED),
                          (curses.COLOR_YELLOW, curses.COLOR_BLUE),
                          (curses.COLOR_BLUE, curses.COLOR_WHITE),
                          (curses.COLOR_WHITE, curses.COLOR_WHITE),
                          (curses.COLOR_BLACK, curses.COLOR_WHITE),
                          (curses.COLOR_GREEN, curses.COLOR_WHITE),
                          (curses.COLOR_WHITE, curses.COLOR_BLACK),
                          (curses.COLOR_RED, curses.COLOR_WHITE), ]

    :ivar list settings: Two list containing the server selection and IP
        protocol version of current session.

        The settings should be like::

            settings = [["Server", 0, []],
                        ["IP Version", 0, ["IPv4", "IPv6"]]]

    :ivar list funckeys: Lists of hot keys with their function to be shown on
        TUI.

        The default :attr:`funckeys` is defined as::

            funckeys = [["", "Select Item"], ["Tab", "Select Field"],
                        ["Enter", "Set Item"], ["F5", "Check Update"],
                        ["F6", "Fetch Update"], ["F10", "Apply Changes"],
                        ["Esc", "Exit"]]

    :ivar list statusinfo: Two lists containing the connection and OS checking
        status of current session.

        The default :attr:`statusinfo` is defined as::

            statusinfo = [["Connection", "N/A", "GREEN"],
                          ["OS", "N/A", "GREEN"]]

    :ivar dict hostsinfo: Containing the `Version`, `Release Date` of current
        hosts data file and the `Latest Version` of the data file on server.

        The default hostsinfo is defined as::

            hostsinfo = {"Version": "N/A", "Release": "N/A", "Latest": "N/A"}

        .. note:: IF the hosts data file does NOT exist in current working
            directory, OR the file metadata has NOT been checked, the values
            here would just be `N/A`.

    :ivar str filename: Filename of the hosts data file containing data to
        make hosts files from. Default by "`hostslist.data`".
    :ivar str infofile: Filename of the info file containing metadata of the
        hosts data file formatted in JSON. Default by "`hostslist.json`".

        .. seealso:: :attr:`filename` and :attr:`infofile` in
            :class:`~gui.hostsutil.HostsUtil` class.

    :ivar str custom: File name of User Customized Hosts File. Customized
        hosts would be able to select if this file exists. The default file
        name is ``custom.hosts``.

        .. seealso:: :ref:`User Customized Hosts<intro-customize>`.
    """
    __title = "HOSTS SETUP UTILITY"
    version = "".join(['v', __version__, ' ', __release__])
    __copyleft = "%s Copyleft 2011-2014, huhamhire-hosts Team" % version

    _stdscr = None
    _item_sup = 0
    _item_inf = 0

    _make_path = "./hosts"
    _funcs = [[], []]
    choice = [[], []]
    slices = [[], []]
    sys_eol = ""

    colorpairs = [(curses.COLOR_WHITE, curses.COLOR_BLUE),
                  (curses.COLOR_WHITE, curses.COLOR_RED),
                  (curses.COLOR_YELLOW, curses.COLOR_BLUE),
                  (curses.COLOR_BLUE, curses.COLOR_WHITE),
                  (curses.COLOR_WHITE, curses.COLOR_WHITE),
                  (curses.COLOR_BLACK, curses.COLOR_WHITE),
                  (curses.COLOR_GREEN, curses.COLOR_WHITE),
                  (curses.COLOR_WHITE, curses.COLOR_BLACK),
                  (curses.COLOR_RED, curses.COLOR_WHITE), ]

    settings = [["Server", 0, []],
                ["IP Version", 0, ["IPv4", "IPv6"]]]
    funckeys = [["", "Select Item"], ["Tab", "Select Field"],
                ["Enter", "Set Item"], ["F5", "Check Update"],
                ["F6", "Fetch Update"], ["F10", "Apply Changes"],
                ["Esc", "Exit"]]
    statusinfo = [["Connection", "N/A", "GREEN"], ["OS", "N/A", "GREEN"]]
    hostsinfo = {"Version": "N/A", "Release": "N/A", "Latest": "N/A"}

    filename = "hostslist.data"
    infofile = "hostsinfo.json"
    custom = "custom.hosts"

    def __init__(self):
        """
        Initialize a new TUI window in terminal.
        """
        locale.setlocale(locale.LC_ALL, '')
        self._stdscr = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        # Set colors
        curses.use_default_colors()
        for i, color in enumerate(self.colorpairs):
            curses.init_pair(i + 1, *color)

    def __del__(self):
        """
        Reset terminal before quit.
        """
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def banner(self):
        """
        Draw the banner in the TUI window.
        """
        screen = self._stdscr.subwin(2, 80, 0, 0)
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
        """
        Draw the footer in the TUI window.
        """
        screen = self._stdscr.subwin(1, 80, 23, 0)
        screen.bkgd(' ', curses.color_pair(1))
        # Set local variable
        normal = curses.A_NORMAL
        # Copyright info
        copyleft = self.__copyleft
        screen.addstr(0, 0, copyleft.center(79), normal)
        screen.refresh()

    def configure_settings_frame(self, pos=None):
        """
        Draw `Configure Setting` frame with a index number (`pos`) of the item
        selected.

        :param pos: Index of selected item in `Configure Setting` frame. The
            default value of `pos` is `None`.
        :type pos: int or None

        .. note:: None of the items in `Configure Setting` frame would be
            selected if pos is `None`.
        """
        self._stdscr.keypad(1)
        screen = self._stdscr.subwin(8, 25, 2, 0)
        screen.bkgd(' ', curses.color_pair(4))
        # Set local variable
        normal = curses.A_NORMAL
        select = curses.color_pair(5)
        select += curses.A_BOLD

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

    def status(self):
        """
        Draw `Status` frame and `Hosts File` frame in the TUI window.
        """
        screen = self._stdscr.subwin(11, 25, 10, 0)
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

    def show_funclist(self, pos, item_sup, item_inf):
        """
        Draw `function selection list` frame with a index number of the item
        selected and the range of items to be displayed.

        :param pos: Index of selected item in `function selection list`.
        :type pos: int or None
        :param item_sup: Upper bound of item index from `function selection
            list`.
        :type item_sup: int
        :param item_inf: Lower bound of item index from `function selection
            list`.
        :type item_inf: int
        """
        # Set UI variable
        screen = self._stdscr.subwin(18, 26, 2, 26)
        screen.bkgd(' ', curses.color_pair(4))
        normal = curses.A_NORMAL
        select = curses.color_pair(5)
        select += curses.A_BOLD
        list_height = 15
        # Set local variable
        ip = self.settings[1][1]
        item_len = len(self.choice[ip])
        # Function list
        items_show = self.choice[ip][item_sup:item_inf]
        items_selec = self._funcs[ip][item_sup:item_inf]
        for p, item in enumerate(items_show):
            sel_ch = '+' if items_selec[p] else ' '
            item_str = ("[%s] %s" % (sel_ch, item[3])).ljust(23)
            item_pos = pos - item_sup if pos is not None else None
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
        if not items_show:
            screen.addstr(4, 2, "No data file!".center(23), normal)
        screen.refresh()
        self._item_sup, self._item_inf = item_sup, item_inf

    def info(self, pos, tab):
        """
        Draw `Information` frame with a index number (`pos`) of the item
        selected from the frame specified by `tab`.

        :param pos: Index of selected item in a specified frame.
        :type pos: int
        :param tab: Index of the frame to select items from.
        :type tab: int

        .. warning:: Both of `pos` and `tab` in this method could not be
            set to `None`.
        """
        screen = self._stdscr.subwin(18, 24, 2, 52)
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
        """
        Draw `Process Bar` at the bottom which is used to indicate progress of
        downloading operation.

        .. note:: This method is a callback function responses to
            :meth:`urllib.urlretrieve` method while fetching hosts data
            file.

        :param done: Block count of packaged retrieved.
        :type done: int
        :param block: Block size of the data pack retrieved.
        :type block: int
        :param total: Total size of the hosts data file.
        :type total: int
        :param mode: A flag indicating the status of `Process Bar`.
            The default value of `mode` is `1`.

            ====  ====================================
            mode  `Process Bar` status
            ====  ====================================
            1     Downloading operation is processing.
            0     Not downloading.
            ====  ====================================
        :type mode: int
        """
        screen = self._stdscr.subwin(2, 80, 20, 0)
        screen.bkgd(' ', curses.color_pair(4))
        normal = curses.A_NORMAL
        line_width = 76
        prog_len = line_width - 20
        # Progress Bar
        if mode:
            done *= block
            prog = 1.0 * prog_len * done / total
            progress = ''.join(['=' * int(prog), '-' * int(2 * prog % 2)])
            progress = progress.ljust(prog_len)
            total = CommonUtil.convert_size(total).ljust(7)
            done = CommonUtil.convert_size(done).rjust(7)
        else:
            progress = ' ' * prog_len
            done = total = 'N/A'.center(7)
        # Show Progress
        prog_bar = "[%s] %s | %s" % (progress, done, total)
        screen.addstr(1, 2, prog_bar, normal)
        screen.refresh()

    def sub_selection_dialog(self, pos):
        """
        Draw a `Selection Dialog` on screen used to make configurations.

        :param pos: Index of selected item in `Configure Setting` frame.
        :type pos: int

        .. warning:: The value of `pos` MUST NOT be `None`.

        :return: A **WindowObject** which represents the selection dialog.
        :rtype: WindowObject
        """
        i_len = len(self.settings[pos][2])
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
        # Title of Subwindow
        screen.addstr(0, 3, self.settings[pos][0].center(12), normal)
        return screen

    def sub_selection_dialog_items(self, pos, i_pos, screen):
        """
        Draw items in `Selection Dialog`.

        :param pos: Index of selected item in `Configure Setting` frame.
        :type pos: int
        :param i_pos: Index of selected item in `Selection Dialog`.
        :type i_pos: int
        :param screen: A **WindowObject** which represents the selection
            dialog.
        :type screen: WindowObject
        """
        # Set local variable
        normal = curses.A_NORMAL
        select = normal + curses.A_BOLD
        for p, item in enumerate(self.settings[pos][2]):
            item_str = item if pos else item["tag"]
            screen.addstr(1 + p, 2, item_str,
                          select if p == i_pos else normal)
        screen.refresh()

    def setup_menu(self):
        """
        Draw the main frame of `Setup` tab in the TUI window.
        """
        screen = self._stdscr.subwin(21, 80, 2, 0)
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
        subtitles = [["Configure Settings", (1, 2)], ["Status", (8, 2)],
                     ["Hosts File", (13, 2)], ["Select Functions", (1, 28)]]
        for s_title in subtitles:
            cord = s_title[1]
            screen.addstr(cord[0], cord[1], s_title[0], title)
            screen.hline(cord[0] + 1, cord[1], curses.ACS_HLINE, 23)
        screen.refresh()

    @staticmethod
    def messagebox(msg, mode=0):
        """
        Draw a `Message Box` with :attr:`msg` in a specified type defined by
        :attr:`mode`.

        .. note:: This is a `static` method.

        :param msg: The information to be displayed in message box.
        :type msg: str
        :param mode: A flag indicating the type of message box to be
            displayed. The default value of `mode` is `0`.

            ====  ===========================================================
            mode  Message Box Type
            ====  ===========================================================
            0     A simple message box showing a message without any buttons.
            1     A message box with an `OK` button for user to confirm.
            2     A message box with `OK` and `Cancel` buttons for user to
                  choose.
            ====  ===========================================================
        :type mode: int
        :return: A flag indicating the choice made by user.

            ======  =====================================================
            Return  Condition
            ======  =====================================================
            0       #. No button is pressed while :attr:`mode` is `0`.
                    #. `OK` button pressed while :attr:`mode` is `1`.
                    #. `Cancel` button pressed while :attr:`mode` is `2`.
            1       `OK` button pressed while :attr:`mode` is `2`.
            ======  =====================================================
        :rtype: int
        """
        pos_x = 24 if mode == 0 else 20
        pos_y = 10
        width = 30 if mode == 0 else 40
        height = 2
        messages = CommonUtil.cut_message(msg, width - 4)
        height += len(messages)
        if mode:
            height += 2
        # Draw Shadow
        shadow = curses.newwin(height, width, pos_y + 1, pos_x + 1)
        shadow.bkgd(' ', curses.color_pair(8))
        shadow.refresh()
        # Draw Subwindow
        screen = curses.newwin(height, width, pos_y, pos_x)
        screen.box()
        screen.bkgd(' ', curses.color_pair(2))
        screen.keypad(1)
        # Set local variable
        normal = curses.A_NORMAL
        select = curses.A_REVERSE
        # Insert messages
        for i in range(len(messages)):
            screen.addstr(1 + i, 2, messages[i].center(width - 4), normal)
        if mode == 0:
            screen.refresh()
        else:
            # Draw subwindow frame
            line_height = 1 + len(messages)
            screen.hline(line_height, 1, curses.ACS_HLINE, width - 2)
            screen.addch(line_height, 0, curses.ACS_SSSB)
            screen.addch(line_height, width - 1, curses.ACS_SBSS)
            tab = 0
            key_in = None
            while key_in != 27:
                if mode == 1:
                    choices = ["OK"]
                elif mode == 2:
                    choices = ["OK", "Cancel"]
                else:
                    return 0
                for i, item in enumerate(choices):
                    item_str = ''.join(['[', item, ']'])
                    tab_pos_x = 6 + 20 * i if mode == 2 else 18
                    screen.addstr(line_height + 1, tab_pos_x, item_str,
                                  select if i == tab else normal)
                screen.refresh()
                key_in = screen.getch()
                if mode == 2:
                    # OK or Cancel
                    if key_in in [9, curses.KEY_LEFT, curses.KEY_RIGHT]:
                        tab = [1, 0][tab]
                    if key_in in [ord('a'), ord('c')]:
                        key_in -= (ord('a') - ord('A'))
                    if key_in in [ord('C'), ord('O')]:
                        return [ord('C'), ord('O')].index(key_in)
                if key_in in [10, 32]:
                    return not tab
            return 0
