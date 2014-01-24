#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _update.py: Retrieve hosts data file.
#
# Copyleft (C) 2013 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import os
import socket
import urllib


class FetchUpdate(object):
    """
    FetchUpdate class contains methods to retrieve the latest hosts data file
    from the project server.

    :ivar str url: The URL of the latest hosts data file.
    :ivar str path: Destination path to save the data file downloaded.
    :ivar str tmp_path: Temporary path to save the data file while
        downloading.
    :ivar int file_size: Size of the data file in bytes.
    :ivar CursesDaemon parent: An instance of
        :class:`~tui.curses_d.CursesDaemon` class to get configuration with.
    """

    def __init__(self, parent):
        """
        Initialize a new instance of this class

        :param parent: An instance of :class:`~tui.curses_d.CursesDaemon`
            class to get configuration with.
        :type parent: :class:`~tui.curses_d.CursesDaemon`
        """
        mirror_id = parent.settings[0][1]
        mirror = parent.settings[0][2][mirror_id]
        self.url = mirror["update"] + parent.filename
        self.path = "./" + parent.filename
        self.tmp_path = self.path + ".download"
        self.file_size = parent._update["size"]
        self.parent = parent

    def get_file(self):
        """
        Fetch the latest hosts data file from project server.
        """
        socket.setdefaulttimeout(10)
        try:
            urllib.urlretrieve(self.url, self.tmp_path,
                               self.parent.process_bar)
            self.replace_old()
        except Exception, e:
            raise e

    def replace_old(self):
        """
        Replace the old hosts data file with the new one.
        """
        if os.path.isfile(self.path):
            os.remove(self.path)
        os.rename(self.tmp_path, self.path)