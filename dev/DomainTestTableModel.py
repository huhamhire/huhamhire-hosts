#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from source_data import SourceData


class DomainTestTableData(QObject):
    def __init__(self, parent=None):
        super(DomainTestTableData, self).__init__(parent)
        self.__domain_id = None
        self._ping_results = []
        self._http_results = []
        self._ping_header = [
            ("", ""), ("IP", "ip"), ("Min", "min"), ("Max", "max"),
            ("Average", "avg"), ("Ratio", "ratio"), ("NS", "ns")
        ]
        self._http_header = [
            ("", ""), ("IP", "ip"), ("Min", "min"), ("Max", "max"),
            ("Average", "avg"), ("Ratio", "ratio"), ("Status", "status"),
            ("NS", "ns")
        ]
        self._summary_header = [
            "", "IP Address", "Ping(ms)", "HTTP/GET(ms)", "HTTP/Status",
            "HTTPS/GET(ms)", "HTTPS/Status", "Name Server"
        ]
        self._selection = {}

        if not SourceData.is_connected:
            SourceData.connect_db()

    def set_domain_id(self, domain_id):
        self.__domain_id = domain_id
        self.get_ping_test_results()
        self.get_http_test_results()
        self.setup_selection()

    def get_ping_test_results(self):
        if self.__domain_id is not None:
            self._ping_results = SourceData.get_ping_results_by_domain_id(
                self.__domain_id
            )

    def get_http_test_results(self):
        if self.__domain_id is not None:
            self._http_results = SourceData.get_http_results_by_domain_id(
                self.__domain_id
            )

    def setup_selection(self):
        for result in self._ping_results:
            self._selection[result["ip"]] = True

    def update_selection(self, ip, status):
        self._selection[ip] = status

    def ping_table_data(self):
        data = []
        if self.__domain_id is None:
            return data
        for result in self._ping_results:
            is_check = self._selection[result["ip"]]
            item = [is_check]
            for tag in self._ping_header[1:]:
                item_data = result[tag[1]]
                if tag[1] == "ns":
                    item_data = item_data.replace("|", ", ").upper()
                    if item_data.endswith(", "):
                        item_data = item_data[:-2]
                if item_data is None:
                    item_data = "N/A"
                item.append(item_data)
            data.append(item)
        return data

    def http_table_data(self, https=False):
        data = []
        if self.__domain_id is None:
            return data
        for result in self._http_results:
            if bool(result["ssl"]) != https:
                continue
            is_check = self._selection[result["ip"]]
            item = [is_check]
            for tag in self._http_header[1:]:
                item_data = result[tag[1]]
                if tag[1] in ["ns", "status"]:
                    item_data = item_data.replace("|", ", ").upper()
                    if item_data.endswith(", "):
                        item_data = item_data[:-2]
                if item_data is None:
                    item_data = "N/A"
                item.append(item_data)
            data.append(item)
        return data

    def summary_table_data(self):
        data = []
        if self.__domain_id is None:
            return data
        for result in self._ping_results:
            item = [None] * len(self._summary_header)
            is_check = self._selection[result["ip"]]
            item[0] = is_check
            item[1] = result["ip"]
            item[2] = result["avg"]
            for http_result in self._http_results:
                if http_result["id"] == result["id"]:
                    if not bool(http_result["ssl"]):
                        item[3] = http_result["avg"]
                        item[4] = http_result["status"]
                    else:
                        item[5] = http_result["avg"]
                        item[6] = http_result["status"]
            item[7] = result["ns"]
            for i in [4, 6, 7]:
                item[i] = item[i].replace("|", ", ").upper()
                if item[i].endswith(", "):
                    item[i] = item[i][:-2]
            for i in [2, 3, 5]:
                if item[i] is None:
                    item[i] = "N/A"
            data.append(item)
        return data

    @property
    def ping_table_header(self):
        header_items = []
        for tag in self._ping_header:
            header_items.append(tag[0])
        return header_items

    @property
    def http_table_header(self):
        header_items = []
        for tag in self._http_header:
            header_items.append(tag[0])
        return header_items

    @property
    def summary_table_header(self):
        return self._summary_header


class DomainTestTableModel(QAbstractTableModel):
    def __init__(self, data_model, parent=None):
        super(DomainTestTableModel, self).__init__(parent)
        self.__table_data = []
        self.__header = []
        self.__checkbox_column = None
        self.__key_column = None
        self._data_model = data_model

    def set_header(self, header):
        self.__header = header

    def set_table_data(self, table_data):
        self.__table_data = table_data

    def set_checkbox_column(self, col):
        self.__checkbox_column = col

    def set_key_column(self, col):
        self.__key_column = col

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.__table_data)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.__header)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            return QVariant(self.__table_data[index.row()][index.column()])

    def setData(self, index, value, role=None):
        box_col = self.__checkbox_column
        key_col = self.__key_column
        if box_col is not None and index.column() == box_col:
            self.__table_data[index.row()][box_col] = value
            ip = self.__table_data[index.row()][key_col]
            self._data_model.update_selection(ip, value)
            return True

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__header[col])
        else:
            return QVariant()

    def flags(self, index):
        # Set CheckBox column
        box_col = self.__checkbox_column
        if box_col is not None and index.column() == box_col:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def sort(self, col, order=Qt.AscendingOrder):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.__table_data = sorted(self.__table_data,
                                   key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.__table_data.reverse()
        self.emit(SIGNAL("layoutChanged()"))


class CheckBoxDelegate(QStyledItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox in every cell of the
    column to which it's applied.
    """
    def __init__(self, parent):
        super(CheckBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this
        cell.
        ** Need to hook up a signal to the model
        """
        return None

    def paint(self, painter, option, index):
        """
        Paint a checkbox without the label.
        """
        checked = index.data().toBool()
        check_box_style_option = QStyleOptionButton()

        if int(index.flags() & Qt.ItemIsEditable) > 0:
            check_box_style_option.state |= QStyle.State_Enabled
        else:
            check_box_style_option.state |= QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off

        check_box_style_option.rect = self.get_box_rect(option)

        self.parent().style().drawControl(
            QStyle.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index):
        """
        Change the data in the model and the state of the checkbox if the user
        presses the left mouse button and this cell is editable.
        Otherwise do nothing.
        """
        if not int(index.flags() & Qt.ItemIsEditable) > 0:
            return False
        # Do not change the checkbox-state
        if event.type() in [QEvent.MouseButtonPress, QEvent.MouseMove,
                            QEvent.MouseButtonDblClick]:
            return False
        if event.type() == QEvent.MouseButtonRelease:
            if event.button() != Qt.LeftButton:
                return False
            if not self.get_box_rect(option).contains(event.pos()):
                return False
        elif event.type() == QEvent.KeyPress:
            if event.key() != Qt.Key_Space and event.key() != Qt.Key_Select:
                return False
        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setModelData(self, editor, model, index):
        new_value = not index.data().toBool()
        model.setData(index, new_value, Qt.EditRole)

    def get_box_rect(self, option):
        style_option = QStyleOptionButton()
        rect = self.parent().style().subElementRect(
            QStyle.SE_CheckBoxIndicator, style_option, None)
        x_pos = option.rect.x() + (option.rect.width() - rect.width()) / 2
        y_pos = option.rect.y() + (option.rect.height() - rect.height()) / 2
        box_point = QPoint(x_pos, y_pos)
        return QRect(box_point, rect.size())


class DomainTestTableWidget(QWidget):
    def __init__(self, table_data, mode="Summary", parent=None, *args):
        super(DomainTestTableWidget, self).__init__(parent, *args)
        self.mode = mode

        self._table_data = table_data
        self._table_model = DomainTestTableModel(self._table_data, self)
        self._table_view = QTableView(self)

        self.set_table_header()
        self._table_model.set_checkbox_column(0)
        self._table_model.set_key_column(1)

        self._table_view.setModel(self._table_model)
        self._table_view.setColumnWidth(0, 30)
        self._table_view.setColumnWidth(1, 150)
        self._table_view.verticalHeader().hide()
        self._table_view.setSortingEnabled(True)
        self._table_view.setSelectionBehavior(self._table_view.SelectRows)
        self.sort_by_col_asc(2)

        self._table_view.setItemDelegateForColumn(
            0, CheckBoxDelegate(self._table_view)
        )

        layout = QVBoxLayout(self)
        layout.setMargin(5)
        layout.addWidget(self._table_view)
        self.setLayout(layout)

    def sort_by_col_asc(self, col):
        self._table_view.sortByColumn(col, Qt.AscendingOrder)

    def set_table_header(self):
        if self.mode == "Summary":
            header = self._table_data.summary_table_header
        elif self.mode == "Ping":
            header = self._table_data.ping_table_header
        elif self.mode == "HTTP" or self.mode == "HTTPS":
            header = self._table_data.http_table_header
        else:
            header = []
        self._table_model.set_header(header)

    def set_table_data(self, domain_id):
        self._table_data.set_domain_id(domain_id)
        self.update_table_data()

    def update_table_data(self):
        if self.mode == "Summary":
            data = self._table_data.summary_table_data()
        elif self.mode == "Ping":
            data = self._table_data.ping_table_data()
        elif self.mode == "HTTP":
            data = self._table_data.http_table_data(False)
        elif self.mode == "HTTPS":
            data = self._table_data.http_table_data(True)
        else:
            data = []
        self._table_model.reset()
        self._table_model.set_table_data(data)


class DomainTestTabWidget(QWidget):
    def __init__(self, parent=None, *args):
        super(DomainTestTabWidget, self).__init__(parent, *args)

        self._table_data = DomainTestTableData(self)

        self.domain_id = None
        self.test_tab = QTabWidget(self)

        self.test_tab.currentChanged.connect(self.update_table_data_by_tab)

        self.tabs = ["Summary", "Ping", "HTTP", "HTTPS"]
        self.test_tables = {}
        for tab in self.tabs:
            self.test_tables[tab] = DomainTestTableWidget(
                self._table_data, tab, self
            )
            self.test_tab.addTab(self.test_tables[tab], tab)

        layout = QVBoxLayout(self)
        layout.setMargin(5)
        layout.addWidget(self.test_tab)

    @pyqtSlot(long)
    def update_table_data_by_domain(self, domain_id):
        self.domain_id = domain_id
        tab_id = self.test_tab.currentIndex()
        table = self.test_tables[self.tabs[tab_id]]
        table.set_table_data(domain_id)
        table.sort_by_col_asc(2)

    @pyqtSlot(int)
    def update_table_data_by_tab(self, tab_id):
        table = self.test_tables[self.tabs[tab_id]]
        table.update_table_data()
