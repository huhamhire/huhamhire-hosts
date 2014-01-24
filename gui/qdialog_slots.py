#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  qdialog_slots.py : Qt slots response to signals on the main dialog.
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

import shutil
import time

from PyQt4 import QtCore, QtGui

from language import LangUtil
from qdialog_d import QDialogDaemon
from util_ui import _translate

import sys
sys.path.append("..")
from util import RetrieveData


class QDialogSlots(QDialogDaemon):
    """
    QDialogSlots class provides `Qt slots` to deal with the `Qt signals`
    emitted by the widgets on the main dialog operated by users.

    .. note:: This class is subclass of :class:`~gui.qdialog_d.QDialogDaemon`
        class and parent class of :class:`~gui.hostsutil.HostsUtil`.

    :ivar int ipv_id: An flag indicating current IP version setting. The
        value could be 1 or 0:

            ======  ==========
            ipv_id  IP Version
            ======  ==========
            1       IPv6
            0       IPv4
            ======  ==========

        .. seealso::
            :meth:`~gui.qdialog_slots.QDialogSlots.on_IPVersion_changed`. in
            this class.

    :ivar str make_path: Temporary path to store generated hosts file. The
        default value of :attr:`make_path` is "`./hosts`".
    :ivar int mirror_id: Index number of current selected server from the
        mirror list.
    """
    _ipv_id = 0

    make_path = "./hosts"
    mirror_id = 0

    def __init__(self):
        """
        Initialize a new instance of this class.
        """
        super(QDialogSlots, self).__init__()

    def reject(self):
        """
        Close this program while the reject signal is emitted.

        .. note:: This method is the slot responses to the reject signal from
            an instance of the main dialog.
        """
        self.close()
        return QtGui.QDialog.reject(self)

    def close(self):
        """
        Close this program while the close signal is emitted.

        .. note:: This method is the slot responses to the close signal from
            an instance of the main dialog.
        """
        try:
            RetrieveData.clear()
        except:
            pass
        super(QDialogDaemon, self).close()

    def mouseMoveEvent(self, e):
        """
        Allow drag operations to set the new position for current cursor.

        :param e: Current mouse event.
        :type e: :class:`PyQt4.QtGui.QMouseEvent`
        """

        if e.buttons() & QtCore.Qt.LeftButton:
            try:
                self.move(e.globalPos() - self.dragPos)
            except AttributeError:
                pass
            e.accept()

    def mousePressEvent(self, e):
        """
        Allow press operation to set the new position for current dialog.

        :param e: Current mouse event.
        :type e: :class:`PyQt4.QtGui.QMouseEvent`
        """
        if e.button() == QtCore.Qt.LeftButton:
            self.dragPos = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

    def on_Mirror_changed(self, mirr_id):
        """
        Change the current server selection.

        .. note:: This method is the slot responses to the signal argument
            :attr:`mirr_id` from SelectMirror widget while the value is
            changed.

        :param mirr_id: Index number of current mirror server.
        """
        self.mirror_id = mirr_id
        self.check_connection()

    def on_IPVersion_changed(self, ipv_id):
        """
        Change the current IP version setting.

        .. note:: This method is the slot responses to the signal argument
            :attr:`ipv_id` from SelectIP widget while the value is changed.

        :param ipv_id: An flag indicating current IP version setting. The
            value could be 1 or 0:

                ======  ==========
                ipv_id  IP Version
                ======  ==========
                1       IPv6
                0       IPv4
                ======  ==========

        :type ipv_id: int
        """
        if self._ipv_id != ipv_id:
            self._ipv_id = ipv_id
            if not RetrieveData.db_exists():
                self.warning_no_datafile()
            else:
                self.set_func_list(0)
                self.refresh_func_list()

    def on_Selection_changed(self, item):
        """
        Change the current selection of modules to be applied to hosts file.

        .. note:: This method is the slot responses to the signal argument
            :attr:`item` from Functionlist widget while the item selection is
            changed.

        :param item: Row number of the item listed in Functionlist which is
            changed by user.
        :type item: int
        """
        ip_flag = self._ipv_id
        func_id = self.ui.Functionlist.row(item)
        if self._funcs[ip_flag][func_id] == 0:
            self._funcs[ip_flag][func_id] = 1
        else:
            self._funcs[ip_flag][func_id] = 0
        mutex = RetrieveData.get_ids(self.choice[ip_flag][func_id][2])
        for c_id, c in enumerate(self.choice[ip_flag]):
            if c[0] == self.choice[ip_flag][func_id][0]:
                if c[1] in mutex and self._funcs[ip_flag][c_id] == 1:
                    self._funcs[ip_flag][c_id] = 0
        self.refresh_func_list()

    def on_Lang_changed(self, lang):
        """
        Change the UI language setting.

        .. note:: This method is the slot responses to the signal argument
            :attr:`lang` from SelectLang widget while the value is changed.

        :param lang: The language name which is selected by user.

            .. note:: This string is typically in the format of IETF language
                tag. For example: en_US, en_GB, etc.

            .. seealso:: :attr:`language` in :class:`~gui.language.LangUtil`
                class.

        :type lang: str
        """
        new_lang = LangUtil.get_locale_by_language(unicode(lang))
        trans = QtCore.QTranslator()
        from hostsutil import LANG_DIR
        trans.load(LANG_DIR + new_lang)
        self.app.removeTranslator(self._trans)
        self.app.installTranslator(trans)
        self._trans = trans
        self.ui.retranslateUi(self)
        self.init_main()
        self.check_connection()

    def on_MakeHosts_clicked(self):
        """
        Start operations to make a hosts file.

        .. note:: This method is the slot responses to the signal from
            ButtonApply widget while the button is clicked.

        .. note:: No operations would be called if current session does not
            have the privileges to change the hosts file.
        """
        if not self._writable:
            self.warning_permission()
            return
        if self.question_apply():
            self.make_path = "./hosts"
            self.make_hosts("system")
        else:
            return

    def on_MakeANSI_clicked(self):
        """
        Export a hosts file encoded in ANSI.

        .. note:: This method is the slot responses to the signal from
            ButtonANSI widget while the button is clicked.
        """
        self.make_path = self.export_hosts()
        if unicode(self.make_path) != u'':
            self.make_hosts("ansi")

    def on_MakeUTF8_clicked(self):
        """
        Export a hosts file encoded in UTF-8.

        .. note:: This method is the slot responses to the signal from
            ButtonUTF widget while the button is clicked.
        """
        self.make_path = self.export_hosts()
        if unicode(self.make_path) != u'':
            self.make_hosts("utf-8")

    def on_Backup_clicked(self):
        """
        Backup the hosts file of current operating system.

        .. note:: This method is the slot responses to the signal from
            ButtonBackup widget while the button is clicked.
        """
        l_time = time.localtime(time.time())
        backtime = time.strftime("%Y-%m-%d-%H%M%S", l_time)
        filename = "hosts_" + backtime + ".bak"
        if self.platform == "OS X":
            filename = "/Users/" + filename
        filepath = QtGui.QFileDialog.getSaveFileName(
            self, _translate("Util", "Backup hosts", None),
            QtCore.QString(filename),
            _translate("Util", "Backup File(*.bak)", None))
        if unicode(filepath) != u'':
            shutil.copy2(self.hosts_path, unicode(filepath))
            self.info_complete()

    def on_Restore_clicked(self):
        """
        Restore a previously backed up hosts file.

        .. note:: This method is the slot responses to the signal from
            ButtonRestore widget while the button is clicked.
            This method would call

        .. note:: No operations would be called if current session does not
            have the privileges to change the hosts file.
        """
        if not self._writable:
            self.warning_permission()
            return
        filename = ''
        if self.platform == "OS X":
            filename = "/Users/" + filename
        filepath = QtGui.QFileDialog.getOpenFileName(
            self, _translate("Util", "Restore hosts", None),
            QtCore.QString(filename),
            _translate("Util", "Backup File(*.bak)", None))
        if unicode(filepath) != u'':
            shutil.copy2(unicode(filepath), self.hosts_path)
            self.info_complete()

    def on_CheckUpdate_clicked(self):
        """
        Retrieve update information (metadata) of the latest data file from a
        specified server.

        .. note:: This method is the slot responses to the signal from
            ButtonCheck widget while the button is clicked.
        """
        if self.choice != [[], []]:
            self.refresh_func_list()
            self.set_update_click_btns()
        if self._update == {} or self._update["version"] == \
            unicode(_translate("Util", "[Error]", None)):
            self.check_update()

    def on_FetchUpdate_clicked(self):
        """
        Retrieve the latest hosts data file.

        .. note:: This method is the slot responses to the signal from
            ButtonUpdate widget while the button is clicked.
            This method would call operations to

        .. note:: Method :meth:`~gui.qdialog_slots.on_CheckUpdate_clicked`
            would be called if no update information has been set,

        .. note:: If the current data is up-to-date, no data file would be
            retrieved.
        """
        self.set_fetch_click_btns()
        self._down_flag = 1
        if self._update == {} or self._update["version"] == \
            unicode(_translate("Util", "[Error]", None)):
            self.check_update()
        elif self.new_version():
            self.fetch_update()
        else:
            self.info_uptodate()
            self.finish_fetch()

    def on_LinkActivated(self, url):
        """
        Open external link in browser.

        .. note:: This method is the slot responses to the signal from a Label
            widget while the text with a hyperlink which is clicked by user.
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))