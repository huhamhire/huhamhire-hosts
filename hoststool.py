#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hoststool.py :
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

from optparse import OptionParser

import gui
import tui

from __version__ import __version__


class UtilLauncher(object):

    @classmethod
    def launch(cls):
        options, args = cls.set_commands()
        if options.tui:
            cls.launch_tui()
        elif options.gui:
            cls.launch_gui()

    @classmethod
    def set_commands(cls):
        usage = "usage: %prog [-g] [-t] [-h] [--version]"
        version = "Hosts Setup Utility v" + __version__
        parser = OptionParser(usage=usage, version=version)
        parser.add_option("-g", "--graphicui", dest="gui",
                          default=True, action="store_true",
                          help="launch in GUI(QT) mode")
        parser.add_option("-t", "--textui", dest="tui",
                          default=False, action="store_true",
                          help="launch in TUI(Curses) mode ")
        return parser.parse_args()

    @classmethod
    def launch_gui(cls):
        main = gui.HostsUtil()
        main.start()

    @classmethod
    def launch_tui(cls):
        main = tui.HostsUtil()
        main.start()

if __name__ == "__main__":
    UtilLauncher.launch()