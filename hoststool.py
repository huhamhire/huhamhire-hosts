#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hoststool.py : Launch the utility.
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

import os

from optparse import OptionParser

import gui
import tui

from __version__ import __version__

import sys
sys.path.append("..")
from util import CommonUtil


class UtilLauncher(object):
    """
    HostsUtil class is the entrance to launch `Hosts Setup Utility`. This
    class contains methods for user to decide whether to start a session in
    Graphical User Interface (GUI) mode or in Text-based User Interface (TUI)
    mode.

    Usage can be printed to screen via terminal by using ``-h`` or ``--help``
    argument. The help message would be like this::

        Usage: hoststool.py [-g] [-t] [-h] [--version]

        Options:
          --version        show program's version number and exit
          -h, --help       show this help message and exit
          -g, --graphicui  launch in GUI(QT) mode
          -t, --textui     launch in TUI(Curses) mode

    .. seealso:: :ref:`Get Started <intro-get-started>`.

    .. note:: All methods from this class are declared as `classmethod`.
    """

    @classmethod
    def launch(cls):
        """
        Launch `Hosts Setup Utility`.

        .. note:: This is a `classmethod`.
        """
        options, args = cls.set_commands()
        if options.tui:
            cls.launch_tui()
        elif options.gui:
            cls.launch_gui()

    @classmethod
    def set_commands(cls):
        """
        Set the command options and arguments to launch `Hosts Setup Utility`.

        .. note:: This is a `classmethod`.

        :return: :meth:`hoststool.UtilLauncher.set_commands` returns two
            values:

            (:attr:`options`, :attr:`args`)

            * options(`optparse.Values`): An instance of
              :class:`optparse.Values` containing values for all of your
              options—e.g. if --file takes a single string argument, then
              options.file will be the filename supplied by the user, or None
              if the user did not supply that option args, the list of
              positional arguments leftover after parsing options.
            * args(`list`): Positional arguments leftover after parsing
              options.

            .. seealso:: `OptionParser
                <http://docs.python.org/2/library/optparse.html>`_.

        :rtype: :class:`optparse.Values`, list
        """
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
        """
        Start a Graphical User Interface (GUI) session of
        `Hosts Setup Utility`.

        .. note:: This is a `classmethod`.
        """
        main = gui.HostsUtil()
        main.start()

    @classmethod
    def launch_tui(cls):
        """
        Start a Text-based User Interface (TUI) session of
        `Hosts Setup Utility`.

        .. note:: This is a `classmethod`.
        """

        # Set code page for Windows
        system = CommonUtil.check_platform()[0]
        cp = "437"
        if system == "Windows":
            chcp = os.popen("chcp")
            cp = chcp.read().split()[-1]
            chcp.close()
            os.popen("chcp 437")

        main = tui.HostsUtil()
        main.start()

        # Restore the default code page for Windows
        if system == "Windows":
            os.popen("chcp " + cp)

if __name__ == "__main__":
    UtilLauncher.launch()