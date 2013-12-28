#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import operator

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class DomainTestTableModel(QAbstractTableModel):
    def __init__(self, test_data, header_data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.__table_data = test_data
        self.__header_data = header_data

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
        if index.column() == 3:
            self.__table_data[index.row()][3] = value
            return True

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__header_data[col])
        else:
            return QVariant()

    def flags(self, index):
        # Set CheckBox column
        if index.column() == 3:
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
        if event.type() in [QEvent.MouseButtonPress, QEvent.MouseMove]:
            return False
        if event.type() in [QEvent.MouseButtonRelease,
                            QEvent.MouseButtonDblClick]:
            if event.button() != Qt.LeftButton:
                return False
            if not self.get_box_rect(option).contains(event.pos()):
                return False
            if event.type() == QEvent.MouseButtonDblClick:
                return False
        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setModelData(self, editor, model, index):
        new_value = not index.data().toBool()
        model.setData(index, new_value, Qt.EditRole)

    def get_box_rect(self, option):
        check_box_style_option = QStyleOptionButton()
        check_box_rect = self.parent().style().subElementRect(
            QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QPoint(option.rect.x() + option.rect.width() / 2 -
                                 check_box_rect.width() / 2,
                                 option.rect.y() + option.rect.height() / 2 -
                                 check_box_rect.height() / 2)
        return QRect(check_box_point, check_box_rect.size())


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.resize(1024, 480)

        table_model = DomainTestTableModel(my_array, header, self)
        table_view = QTableView()
        table_view.setModel(table_model)
        table_view.setColumnWidth(0, 200)
        table_view.setColumnWidth(3, 30)
        table_view.verticalHeader().hide()
        table_view.setSortingEnabled(True)

        table_view.setItemDelegateForColumn(3, CheckBoxDelegate(table_view))

        layout = QVBoxLayout(self)

        layout.addWidget(table_view)
        self.setLayout(layout)


my_array = [['00', '01', '02', True],
            ['10', '11', '12', True],
            ['20', '21', '22', False],
            ['30', '31', 'N/A', False],
            ]
header = ["IP", "Ping", "HTTP", "Chk"]


def main():
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()