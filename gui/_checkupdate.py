#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _checkupdate.py: Check update info of the latest data file.
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
    """
    QSubChkConnection is a subclass of :class:`PyQt4.QtCore.QThread`. This
    class contains methods to retrieve the metadata of the latest hosts data
    file.

    .. inheritance-diagram:: gui._checkupdate.QSubChkUpdate
        :parts: 1

    .. note:: The instance of this class should be created in an individual
        thread. And an instance of  class should be set as :attr:`parent`
        here.

    :ivar PyQt4.QtCore.pyqtSignal trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to emit signal to the main dialog
        which indicates current status.

        .. note:: The signal :attr:`trigger` should be a dictionary (`dict`)
            containing metadata of the latest hosts data file.

        .. seealso:: Method :meth:`~gui.qdialog_d.QDialogDaemon.finish_update`
            in :class:`~gui.qdialog_d.QDialogDaemon` class.
    """
    trigger = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        """
        Initialize a new instance of this class. Retrieve mirror settings from
        the main dialog to check the update information.


        :param parent: An instance of :class:`~gui.qdialog_d.QDialogDaemon`
            class to fetch settings from.
        :type parent: :class:`~gui.qdialog_d.QDialogDaemon`

        .. warning:: :attr:`parent` MUST NOT be set as `None`.
        """
        super(QSubChkUpdate, self).__init__(parent)
        self.url = parent.mirrors[parent.mirror_id]["update"] + parent.infofile

    def run(self):
        """
        Start operations to retrieve the metadata of the latest hosts data
        file.
        """
        try:
            socket.setdefaulttimeout(5)
            urlobj = urllib.urlopen(self.url)
            j_str = urlobj.read()
            urlobj.close()
            info = json.loads(j_str)
            self.trigger.emit(info)
        except:
            info = {"version": unicode(_translate("Util", "[Error]", None))}
            self.trigger.emit(info)