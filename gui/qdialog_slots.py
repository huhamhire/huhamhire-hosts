#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  qdialog_slots.py :
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
    Attributes:
        _ipv_id (int): An integer indicating current IP version setting. The
            value could be 1 or 0. 1 represents IPv6 while 1 represents IPv4.

        make_path (str): A string indicating the path to store the hosts file
            in export mode.
        mirror_id (int): An integer indicating current index number of
            mirrors.
    """
    _ipv_id = 0

    make_path = "./hosts"
    mirror_id = 0

    def __init__(self):
        """Initialize a new instance of this class - Private Method
        """
        super(QDialogSlots, self).__init__()

    def mouseMoveEvent(self, e):
        """Set mouse drag event - Public Method

        Allow drag operations to set the new position for current dialog.

        Args:
            e (QMouseEvent): A QMouseEvent object indicating current mouse
                event.
        """
        if e.buttons() & QtCore.Qt.LeftButton:
            try:
                self.move(e.globalPos() - self.dragPos)
            except AttributeError:
                pass
            e.accept()

    def mousePressEvent(self, e):
        """Set mouse press event - Public Method

        Allow drag operations to set the new position for current dialog.

        Args:
            e (QMouseEvent): A QMouseEvent object indicating current mouse
                event.
        """
        if e.button() == QtCore.Qt.LeftButton:
            self.dragPos = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

    def on_Mirror_changed(self, mirr_id):
        """Change the current mirror setting - Public Method

        The slot response to the signal ({mirr_id}) from SelectMirror widget
        while the value is changed.

        Args:
            mirr_id (int): An integer indicating current index number of
                mirrors.
        """
        self.mirror_id = mirr_id
        self.check_connection()

    def on_IPVersion_changed(self, ipv_id):
        """Change the current IP version setting - Public Method

        The slot response to the signal ({ipv_id}) from SelectIP widget while
        the value is changed.

        Args:
            ipv_id (int): An integer indicating current IP version setting.
                The value could be 1 or 0. 1 represents IPv6 while 1
                represents IPv4.
        """
        if self._ipv_id != ipv_id:
            self._ipv_id = ipv_id
            if not RetrieveData.db_exists():
                self.warning_no_datafile()
            else:
                self.set_func_list(0)
                self.refresh_func_list()

    def on_Selection_changed(self, item):
        """Change the function selection setting - Public Method

        The slot response to the signal ({item}) from Functionlist widget
        while the selection of the items is changed. This method would change
        the current selection of functions.

        Args:
            item (int): An integer indicating the row number of the item
                listed in Functionlist which is changed by user.
        """
        ip_flag = self._ipv_id
        func_id = item.listWidget().row(item)
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
        """Change the UI language setting - Public Method

        The slot response to the signal ({lang}) from SelectLang widget while
        the value is changed. This method would change the language of the UI.

        Args:
            lang (str): A string indicating the language which is selected by
                user.
                This string uses the for of IETF language tag. For example:
                en_US, en_GB, etc.
        """
        new_lang = LangUtil.get_locale_by_language(unicode(lang))
        trans = QtCore.QTranslator()
        from hostsutil import LANG_DIR
        trans.load(LANG_DIR + new_lang)
        QtGui.QApplication.removeTranslator(self._trans)
        QtGui.QApplication.installTranslator(trans)
        self._trans = trans
        self.Ui.retranslateUi(self)
        self.init_main()
        self.check_connection()

    def on_MakeHosts_clicked(self):
        """Start making hosts file - Public Method

        The slot response to the signal from ButtonApply widget while the
        button is clicked. This method would call operations to make a hosts
        file.
        No operations would be called if current session does not have the
        privileges to change the hosts file.
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
        """Export hosts ANSI - Public Method

        The slot response to the signal from ButtonANSI widget while the
        button is clicked. This method would call operations to export a hosts
        file encoding in ANSI.
        """
        self.make_path = self.export_hosts()
        if unicode(self.make_path) != u'':
            self.make_hosts("ansi")

    def on_MakeUTF8_clicked(self):
        """Export hosts in UTF-8 - Public Method

        The slot response to the signal from ButtonUTF widget while the
        button is clicked. This method would call operations to export a hosts
        file encoding in UTF-8.
        """
        self.make_path = self.export_hosts()
        if unicode(self.make_path) != u'':
            self.make_hosts("utf-8")

    def on_Backup_clicked(self):
        """Backup system hosts file - Public Method

        The slot response to the signal from ButtonBackup widget while the
        button is clicked. This method would call operations to backup the
        hosts file of current operating system.
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
        """Restore hosts file - Public Method

        The slot response to the signal from ButtonRestore widget while the
        button is clicked. This method would call operations to restore a
        previously backed up hosts file.
        No operations would be called if current session does not have the
        privileges to change the hosts file.
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
        """Check data file update - Public Method

        The slot response to the signal from ButtonCheck widget while the
        button is clicked. This method would call operations to fetch update
        information of the latest data file.
        """
        if self.choice != [[], []]:
            self.refresh_func_list()
            self.set_update_click_btns()
        if self._update == {} or self._update["version"] == \
            unicode(_translate("Util", "[Error]", None)):
            self.check_update()

    def on_FetchUpdate_clicked(self):
        """Fetch data file update - Public Method

        The slot response to the signal from ButtonUpdate widget while the
        button is clicked. This method would call operations to fetch the
        latest data file.
        If no update information has been got from the server, the method to
        check the update would be called.
        If the current data is up-to-date, no data file would be retrieved.
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
        """Open external link in browser - Public Method

        The slot response to the signal from Label widget while the text with
        a hyperlink is clicked by user.
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))