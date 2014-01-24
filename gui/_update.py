#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _update.py: Fetch the latest data file.
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
    """
    QSubFetchUpdate is a subclass of :class:`PyQt4.QtCore.QThread`. This
    class contains methods to retrieve the latest hosts data file from a
    server.

    .. inheritance-diagram:: gui._update.QSubFetchUpdate
        :parts: 1

    .. note:: The instance of this class should be created in an individual
        thread. And an instance of  class should be set as :attr:`parent`
        here.

    :ivar PyQt4.QtCore.pyqtSignal prog_trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to emit signal to the main dialog
        which indicates current downloading progress.

        .. note:: The signal :attr:`prog_trigger` should be a tuple of
            (`progress`, message`):

            * progress(`int`): An number between `0` and `100` which indicates
              current download progress.
            * message(`str`): Message to be displayed to users on the progress
              bar.

    :ivar PyQt4.QtCore.pyqtSignal finish_trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to emit signal to the main dialog
        which notifies if current operation is finished.

        .. note:: The signal :attr:`finish_trigger` should be a tuple of
            (`refresh_flag`, error_flag`):

            * refresh_flag(`int`): An flag indicating whether to refresh
              function list in the main dialog or not.

                ============  ==============
                refresh_flag  Operation
                ============  ==============
                1             Refresh
                0             Do not refresh
                ============  ==============
            * error_flag(`int`): An flag indicating whether the downloading
              progress is successfully finished or not.

                ==========  =======
                error_flag  Status
                ==========  =======
                1           Error
                0           Success
                ==========  =======

        .. seealso:: Method :meth:`~gui.qdialog_d.QDialogDaemon.finish_fetch`
            in :class:`~gui.qdialog_d.QDialogDaemon` class.

    """
    prog_trigger = QtCore.pyqtSignal(int, str)
    finish_trigger = QtCore.pyqtSignal(int, int)

    def __init__(self, parent):
        """
        Initialize a new instance of this class. Fetch download settings from
        the main dialog to retrieve new hosts data file.

        :param parent: An instance of :class:`~gui.qdialog_d.QDialogDaemon`
            class to fetch settings from.
        :type parent: :class:`~gui.qdialog_d.QDialogDaemon`

        .. warning:: :attr:`parent` MUST NOT be set as `None`.
        """
        super(QSubFetchUpdate, self).__init__(parent)
        self.url = parent.mirrors[parent.mirror_id]["update"] + \
            parent.filename
        self.path = "./" + parent.filename
        self.tmp_path = self.path + ".download"
        self.filesize = parent._update["size"]

    def run(self):
        """
        Start operations to retrieve the new hosts data file.
        """
        self.prog_trigger.emit(0, unicode(_translate(
            "Util", "Connecting...", None)))
        self.fetch_file()

    def fetch_file(self):
        """
        Retrieve the latest data file to a specified local path with a url.
        """
        socket.setdefaulttimeout(10)
        try:
            urllib.urlretrieve(self.url, self.tmp_path, self.set_progress)
            self.replace_old()
            self.finish_trigger.emit(1, 0)
        except:
            self.finish_trigger.emit(1, 1)

    def set_progress(self, done, block, total):
        """
        Send message to the main dialog to set the progress bar.

        :param done: Block count of packaged retrieved.
        :type done: int
        :param block: Block size of the data pack retrieved.
        :type block: int
        :param total: Total size of the hosts data file.
        :type total: int
        """
        done = done * block
        if total <= 0:
            total = self.filesize
        prog = 100 * done / total
        done = CommonUtil.convert_size(done)
        total = CommonUtil.convert_size(total)
        text = unicode(_translate(
            "Util", "Downloading: %s / %s", None)) % (done, total)
        self.prog_trigger.emit(prog, text)

    def replace_old(self):
        """
        Replace the old hosts data file with the new one.
        """
        if os.path.isfile(self.path):
            os.remove(self.path)
        os.rename(self.tmp_path, self.path)