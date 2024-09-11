import sys
import cv2
import os
import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from HomePages.settings_ui import Ui_SettingsWindow
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QImage, QIcon
import Resources.resources_rc
import Components.QSwitchButton
from Scripts import json_unit

# ignore the "Sig..."
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class SettingsWindow(QtWidgets.QWidget, Ui_SettingsWindow):
    chooseSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(':/settings2'))
        self.initUI()
        self.updateSettings()

    def initUI(self):
        # self.setLayout(self.gridLayout)
        # self.pushButton.clicked.connect(lambda: self.textEdit.clear())
        self.cancleButton.clicked.connect(lambda: self.updateSettings(1))
        self.saveButton.clicked.connect(lambda: self.updateSettings(2))
        self.restoreButton.clicked.connect(lambda: self.updateSettings(3))

    def updateSettings(self, index=0):
        current_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
        json_file_path = os.path.join(current_directory, 'Config', 'settings.json')
        last_settings = json_unit.json_read(json_file_path)

        # 默认打开settings.json更新配置，刷新界面
        if index == 0:
            self.traysize_CB.setCurrentIndex(int(last_settings["tray_size"]))
            self.selectedSeeds_CB.setCurrentIndex(int(last_settings["selected_seed"]))
            self.interval_CB.setCurrentIndex(int(last_settings["detection_interval"]))

        # 点击取消按钮
        elif index == 1:
            self.close()

        # 点击保存按钮
        elif index == 2:
            last_settings["tray_size"] = self.traysize_CB.currentIndex()
            last_settings["selected_seed"] = self.selectedSeeds_CB.currentIndex()
            last_settings["detection_interval"] = self.interval_CB.currentIndex()
            json_unit.json_write(json_file_path, last_settings)
            self.chooseSignal.emit("saveButton clicked")
            self.close()

        # 点击恢复按钮
        elif index == 3:
            self.traysize_CB.setCurrentIndex(0)
            self.selectedSeeds_CB.setCurrentIndex(0)
            self.interval_CB.setCurrentIndex(0)

        else:
            print("Error: None of such index exists")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    setW = SettingsWindow()
    setW.show()
    sys.exit(app.exec_())