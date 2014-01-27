#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _make.py: Make a new hosts file.
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import time
from PyQt4 import QtCore

import sys
sys.path.append("..")
from util import RetrieveData
from util import MakeHosts


class QSubMakeHosts(QtCore.QThread, MakeHosts):
    """
    QSubMakeHosts is a subclass of :class:`PyQt4.QtCore.QThread` and class
    :class:`~util.makehosts.MakeHosts`. This class contains methods to make a
    new hosts file for client.

    .. inheritance-diagram:: gui._make.QSubMakeHosts
        :parts: 1

    .. note:: The instance of this class should be created in an individual
        thread. And an instance of class should be set as :attr:`parent`
        here.

    :ivar PyQt4.QtCore.pyqtSignal info_trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to emit signal to the main dialog
        which indicates the current operation.

        .. note:: The signal :attr:`info_trigger` should be a tuple of
            (`mod_name`, mod_num`):

            * mod_name(`str`): Tag of a specified hosts module in current
              progress.
            * mod_num(`int`): Number of current module in the operation
              sequence.

        .. seealso:: Method
            :meth:`~gui.qdialog_ui.QDialogUI.set_make_progress`
            in :class:`~gui.qdialog_ui.QDialogUI` class.

    :ivar PyQt4.QtCore.pyqtSignal fina_trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to emit signal to the main dialog
        which notifies statistics to the main dialog.

        .. note:: The signal :attr:`fina_trigger` should be a tuple of
            (`time`, count`):

            * time(`str`): Total time uesd while generating the new hosts
              file.
            * count(`int`): Total number of hosts entries inserted into the
              new hosts file.

        .. seealso:: Method :meth:`~gui.qdialog_d.QDialogDaemon.finish_make`
            in :class:`~gui.qdialog_d.QDialogDaemon` class.

    :ivar PyQt4.QtCore.pyqtSignal move_trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to notify the main dialog while new
        hosts is being moved to specified path on current operating system.

        .. note:: This signal does not send any data.

        .. seealso:: Method :meth:`~gui.qdialog_d.QDialogDaemon.move_hosts`
            in :class:`~gui.qdialog_d.QDialogDaemon` class.

    .. seealso:: :class:`util.makehosts.MakeHosts` class.
    """
    info_trigger = QtCore.pyqtSignal(str, int)
    fina_trigger = QtCore.pyqtSignal(str, int)
    move_trigger = QtCore.pyqtSignal()

    def __init__(self, parent):
        """
        Initialize a new instance of this class. Retrieve configuration from
        the main dialog to make a new hosts file.

        :param parent: An instance of :class:`~gui.qdialog_d.QDialogDaemon`
            class to fetch settings from.
        :type parent: :class:`~gui.qdialog_d.QDialogDaemon`

        .. warning:: :attr:`parent` MUST NOT be set as `None`.
        """
        QtCore.QThread.__init__(self, parent)
        MakeHosts.__init__(self, parent)

    def run(self):
        """
        Start operations to retrieve data from the data file and generate new
        hosts file.
        """
        start_time = time.time()
        self.make()
        end_time = time.time()
        total_time = "%.4f" % (end_time - start_time)
        self.fina_trigger.emit(total_time, self.count)
        if self.make_mode == "system":
            self.move_trigger.emit()

    def get_hosts(self, make_cfg):
        """
        Make the new hosts file by the configuration defined by `make_cfg`
        from function list on the main dialog.

        :param make_cfg: Module settings in byte word format.
        :type make_cfg: dict

        .. seealso:: :attr:`make_cfg` in :class:`~tui.curses_d.CursesDaemon`
            class.
        """
        for part_id in sorted(make_cfg.keys()):
            mod_cfg = make_cfg[part_id]
            if not RetrieveData.chk_mutex(part_id, mod_cfg):
                return
            mods = RetrieveData.get_ids(mod_cfg)
            for mod_id in mods:
                self.mod_num += 1
                hosts, mod_name = RetrieveData.get_host(part_id, mod_id)
                self.info_trigger.emit(mod_name, self.mod_num)
                if part_id == 0x02:
                    self.write_localhost_mod(hosts)
                elif part_id == 0x04:
                    self.write_customized()
                else:
                    self.write_common_mod(hosts, mod_name)
