import sys
import cv2
import os
import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from HomePages.export_ui import Ui_ExportDialog
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QImage, QIcon
import Resources.resources_rc
import Components.QSwitchButton
from Scripts.sqlite_unit import *


# ignore the "Sig..."
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class ExportPage(QtWidgets.QMainWindow, Ui_ExportDialog):
    chooseSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.cancleButton.clicked.connect(lambda: self.save2Local(0))
        self.saveButton.clicked.connect(lambda: self.save2Local(1))
        self.updateUI()

    def updateUI(self):
        # 加载数据库中表，同步更新datalistUI
        conn = sqlite3.connect('test.db')
        dataList = get_tables(conn)
        # print(dataList)
        self.dataItemList.addItems(dataList)
        conn.close()

    def save2Local(self, bt_type=0):
        """

        :param bt_type:
        :return:
        """
        if bt_type == 0:
            self.close()
        elif bt_type == 1:
            savePath = self.pathText.text()
            name = self.filenameText.text()
            path = savePath + "\\" + name  # 获取列表选中的路径和文件名字
            text_list = self.dataItemList.selectedItems()  # 获取列表选中的数据
            conn = sqlite3.connect('test.db')

            if len(text_list) != 0:
                for item in list(text_list):
                    export_to_xlsx(conn, path + item.text(), item.text())
                    # print(item.text())

            conn.close()
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    setW = ExportPage()
    setW.show()
    sys.exit(app.exec_())
