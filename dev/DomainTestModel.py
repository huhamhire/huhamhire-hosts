#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import operator

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from source_data import SourceData


class DomainTestTableData(object):
    def __init__(self, domain_id):
        self.__domain_id = domain_id
        self._ping_results = []
        self._ping_header = [
            ("", ""), ("IP", "ip"), ("Min", "min"), ("Max", "max"),
            ("Average", "avg"), ("Ratio", "ratio"), ("NS", "ns")]
        self.get_ping_test_results()

    def get_ping_test_results(self):
        SourceData.connect_db()
        self._ping_results = SourceData.get_ping_test_results_by_domain_id(
            self.__domain_id)

    @property
    def ping_test_data(self):
        data = []
        for result in self._ping_results:
            is_check = 0
            item = [is_check]
            for tag in self._ping_header[1:]:
                item_data = result[tag[1]]
                if tag[1] == "ns":
                    item_data = item_data.replace("|", ", ")
                if item_data is None:
                    item_data = "N/A"
                item.append(item_data)
            data.append(item)
        return data

    @property
    def ping_test_header(self):
        header_items = []
        for tag in self._ping_header:
            header_items.append(tag[0])
        return header_items


class DomainTestTableModel(QAbstractTableModel):
    def __init__(self, table_data, header_data, checkbox=None, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.__table_data = table_data
        self.__header_data = header_data
        self.__checkbox_column = checkbox

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.__table_data)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.__table_data[0])

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            return QVariant(self.__table_data[index.row()][index.column()])

    def setData(self, index, value, role=None):
        box_col = self.__checkbox_column
        if box_col is not None and index.column() == box_col:
            self.__table_data[index.row()][box_col] = value
            return True

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__header_data[col])
        else:
            return QVariant()

    def flags(self, index):
        # Set CheckBox column
        box_col = self.__checkbox_column
        if box_col is not None and index.column() == box_col:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled

    def sort(self, col, order=None):
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
        QStyledItemDelegate.__init__(self, parent)

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


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.resize(1024, 480)

        table_data = DomainTestTableData(169048887)
        data = table_data.ping_test_data
        header = table_data.ping_test_header

        table_model = DomainTestTableModel(data, header, 0, self)
        table_view = QTableView()
        table_view.setModel(table_model)
        table_view.setColumnWidth(0, 30)
        table_view.setColumnWidth(1, 200)
        table_view.verticalHeader().hide()
        table_view.setSortingEnabled(True)

        table_view.setItemDelegateForColumn(0, CheckBoxDelegate(table_view))

        layout = QVBoxLayout(self)

        layout.addWidget(table_view)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()