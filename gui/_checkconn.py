#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _checkconn.py: Check connect to a specified server.
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
    """
    QSubChkConnection is a subclass of :class:`PyQt4.QtCore.QThread`. This
    class contains methods to check the network connection with a specified
    server.

    .. inheritance-diagram:: gui._checkconn.QSubChkConnection
        :parts: 1

    .. note:: The instance of this class should be created in an individual
        thread. And an instance of  class should be set as :attr:`parent`
        here.

    :ivar PyQt4.QtCore.pyqtSignal trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to emit signal to the main dialog
        which indicates current status.

        .. note:: The signal :attr:`trigger` should be a integer flag:

            ======  ========
            signal  Status
            ======  ========
            -1      Checking
            0       Failed
            1       OK
            ======  ========
    """
    trigger = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        """
        Initialize a new instance of this class. Retrieve mirror settings from
        the main dialog to check the connection.

        :param parent: An instance of :class:`~gui.qdialog_d.QDialogDaemon`
            class to fetch settings from.
        :type parent: :class:`~gui.qdialog_d.QDialogDaemon`

        .. warning:: :attr:`parent` MUST NOT be set as `None`.
        """
        super(QSubChkConnection, self).__init__(parent)
        self.link = parent.mirrors[parent.mirror_id]["test_url"]

    def run(self):
        """
        Start operations to check the network connection with a specified
        server.
        """
        self.trigger.emit(-1)
        status = CommonUtil.check_connection(self.link)
        self.trigger.emit(status)