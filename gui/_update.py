#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _update.py:
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import os
import socket
import urllib
from PyQt4 import QtCore

from util_ui import _translate

import sys
sys.path.append("..")
from util import CommonUtil


class QSubFetchUpdate(QtCore.QThread):
    """A class to fetch the latest data file

    QSubFetchUpdate is a subclasse of PyQt4.QtCore.QThread. This class
    contains methods to retrieve the latest hosts data file.

    The instance of this class should be created in an individual thread. And
    the object instance of HostsUtil class should be set as parent here.

    Attributes:
        prog_trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit progress
            signal to the main dialog indicating the current download
            progress. The meaning of the signal arguments is listed here:
                (int, str) -> (progress, message)
                progress (int): An integer indicating the current download
                    progress.
                message (str): A string indicating the message to be shown to
                    users on the progress bar.
        finish_trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit finish
            signal to the main dialog. The meaning of the signal arguments is
            listed here:
                (int, int) -> (refresh_flag, error_flag)
                refresh_flag (int): An integer indicating whether to refresh
                    the funcion list or not. 1: refresh, 0: do not refresh.
                error_flag (int): An integer indicating whether the
                    downloading is successfully finished or not.
                    1: error, 0: success.
    """
    prog_trigger = QtCore.pyqtSignal(int, str)
    finish_trigger = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Get download settings from the main dialog to retrieve new hosts data
        file.

        Args:
            parent (obj): An instance of HostsUtil object to get settings
                from.
        """
        super(QSubFetchUpdate, self).__init__(parent)
        self.url = parent.mirrors[parent._mirr_id]["update"] + parent.filename
        self.path = "./" + parent.filename
        self.tmp_path = self.path + ".download"
        self.filesize = parent._update["size"]

    def run(self):
        """Fetch data file - Public Method

        Operations to retrieve the new hosts data file.
        """
        self.prog_trigger.emit(0, unicode(_translate(
            "Util", "Connecting...", None)))
        self.fetch_file()

    def fetch_file(self):
        """Fetch the data file - Public Method

        Retrieve the latest data file to a specified path ({path}) by url
        ({url}).

        Args:
            url (str): A string indicating the url to fetch the latest data
                file.
            path (str): A string indicating the path to save the data file on
                current machine.
        """
        socket.setdefaulttimeout(10)
        try:
            urllib.urlretrieve(self.url, self.tmp_path, self.set_progress)
            self.replace_old()
            self.finish_trigger.emit(1, 0)
        except:
            self.finish_trigger.emit(1, 1)

    def set_progress(self, done, blocksize, total):
        """Set progress bar in the main dialog - Public Method

        Send message to the main dialog to set the progress bar Prog.

        Args:
            done (int): An integer indicating the number of data blocks have
                been downloaded from the server.
            blocksize (int): An integer indicating the size of a data block.
        """
        done = done * blocksize
        if total <= 0:
            total = self.filesize
        prog = 100 * done / total
        done = CommonUtil.convert_size(done)
        total = CommonUtil.convert_size(total)
        text = unicode(_translate(
            "Util", "Downloading: %s / %s", None)) % (done, total)
        self.prog_trigger.emit(prog, text)

    def replace_old(self):
        """Replace the old data file - Public Method

        Overwrite the old hosts data file with the new one.
        """
        if os.path.isfile(self.path):
            os.remove(self.path)
        os.rename(self.tmp_path, self.path)