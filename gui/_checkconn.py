#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _checkconn.py:
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

from PyQt4 import QtCore

import sys
sys.path.append("..")
from util import CommonUtil


class QSubChkConnection(QtCore.QThread):
    """A class to check connection with server

    QSubChkConnection is a subclasse of PyQt4.QtCore.QThread. This class
    contains methods to check the network connection with a specified mirror.

    The instance of this class should be created in an individual thread. And
    the object instance of HostsUtil class should be set as parent here.

    Attribute:
        trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit suatus signal
            to the main dialog. The meaning of the signal arguments is listed
            here:
                -1 -> checking..., 0 -> Failed, 1 -> OK.
    """
    trigger = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Get mirror settings from the main dialog to check the connection.

        Args:
            parent (obj): An instance of HostsUtil object to get settings
                from.
        """
        super(QSubChkConnection, self).__init__(parent)
        self.link = parent.mirrors[parent._mirr_id]["test_url"]

    def run(self):
        """Check connection - Public Method

        Operations to check the network connection with a specified mirror.
        """
        self.trigger.emit(-1)
        status = CommonUtil.check_connection(self.link)
        self.trigger.emit(status)