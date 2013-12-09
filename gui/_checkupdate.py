#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _checkupdate.py:
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import json
import socket
import urllib
from PyQt4 import QtCore

from util_ui import _translate


class QSubChkUpdate(QtCore.QThread):
    """A class to check update info of the latest data file

    QSubChkConnection is a subclasse of PyQt4.QtCore.QThread. This class
    contains methods to retrieve the metadata of the latest hosts data file.

    The instance of this class should be created in an individual thread. And
    the object instance of MainDialog class should be set as parent here.

    Attribute:
        trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit suatus signal
            to the main dialog. The meaning of the signal is listed here:
                (dict) -> (update_info)
                update_info (dict): A dictionary containing metadata of the
                    latest hosts data file.
    """
    trigger = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Get mirror settings from the main dialog to check the connection.

        Args:
            parent (obj): An instance of MainDialog object to get settings
                from.
        """
        super(QSubChkUpdate, self).__init__(parent)
        self.url = parent.mirrors[parent._mirr_id]["update"] + parent.infofile

    def run(self):
        """Check update - Public Method

        Operations to retrieve the metadata of the latest hosts data file.
        """
        try:
            socket.setdefaulttimeout(5)
            urlobj = urllib.urlopen(self.url)
            j_str = urlobj.read()
            urlobj.close()
            info = json.loads(j_str)
            self.trigger.emit(info)
        except:
            info = {"version": unicode(_translate("HostsUtlMain",
                                    "[Error]", None))}
            self.trigger.emit(info)