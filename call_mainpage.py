import random
import sys
import cv2
import os
import time
import sqlite3
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QImage, QIcon
from threading import Thread
import Resources.resources_rc
import Components.QSwitchButton
from HomePages.mainpage_ui import Ui_MainWindow
from call_exportpage import ExportPage
from call_settingspage import SettingsWindow
from Scripts import json_unit, sqlite_unit

from queue import Queue
import threading
import time, random
import torch
from ultralytics import YOLO
lock = threading.Lock()

# ignore the "Sig..."
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def async_call(fn):
    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class MainPageWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    chooseSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MainPageWindow, self).__init__(parent)

        # 创建线程

        self.setupUi(self)
        self.setWindowIcon(QIcon(':/seed'))
        self.cameraTimer = QTimer()
        self.switchButton = Components.QSwitchButton.SwitchButton(parent=self)
        self.settingsWindow = SettingsWindow()
        self.exportDialog = ExportPage()

        self.model = YOLO(r'..\weights\best.pt').to('cuda' if torch.cuda.is_available() else 'cpu')
        self.frame_queue = Queue(maxsize=1)

        self.initUI()

    def initUI(self):

        # self.pushButton.clicked.connect(lambda: self.textEdit.clear())
        self.pb_export.clicked.connect(self.exportData)
        self.pb_settings.clicked.connect(self.showSettingsWindow)
        self.switchButton.switch_toggled.connect(self.switchChanged)
        self.switchButton.move(15, 68)
        self.update()

    def update(self):
        try:
            conn = sqlite3.connect('test.db')
            sqlite_unit.create_table(conn)
            conn.close()
            print("ready!")
        except:
            pass
        last_settings = json_unit.json_read(r"./Config/settings.json")
        self.changeIcon(0, seed_index=int(last_settings["selected_seed"]))

        # ToDo 参数设置窗口设置后的参数更新；

    def exportData(self):
        self.exportDialog.setWindowModality(Qt.ApplicationModal)
        self.exportDialog.show()

    def showSettingsWindow(self):
        self.settingsWindow.setWindowModality(Qt.ApplicationModal)
        self.settingsWindow.chooseSignal.connect(self.update)
        self.settingsWindow.updateSettings()
        self.settingsWindow.show()

    def switchChanged(self):
        """ 开关按钮选中状态改变的槽函数 """
        isChecked = self.switchButton.isChecked()

        self.setEnableStatus(isChecked)  # 设置面板控件是使能状态
        self.changeIcon(1, switchOn=isChecked)  # 改变开关按钮图标

        self.startDetectionThread()  # 开始调用检测模型
        self.textUpdateThread()  # 实时刷新显示监测结果
        self.showVideoThread(isChecked)  # 调用显示视频函数

    @async_call
    def startDetectionThread(self):
        try:
            # 创建数据库链接
            conn = sqlite3.connect('test.db')
            rc = sqlite_unit.get_table_row_counts(conn, 1)
            for i in range(10):
                # list = []
                sn = rc + i + 1
                sr = round(random.uniform(90, 98), 2)
                rr = round(random.uniform(2, 6), 2)
                mr = round(random.uniform(3, 5), 2)
                tc = round(random.uniform(2, 4), 2)
                # list.append([sn, sr, rr, mr, tc])
                sqlite_unit.insert_data(conn, [[sn, sr, rr, mr, tc],[sn, sr, rr, mr, tc]], 1)

            while True:
                if not self.switchButton.isChecked():
                    break

                results = sqlite_unit.get_ave_values(conn)  # 数据均值计算
                if len(results) > 0:
                    self.lb_number_dn.setText(str(results[0]))
                    self.lb_number_asr.setText(str(results[1]) + "%")
                    self.lb_number_arr.setText(str(results[2]) + "%")
                    self.lb_number_amr.setText(str(results[3]) + "%")

            # ToDo 载入检测模型

            conn.close()
        except:
            pass

    @async_call
    def textUpdateThread(self):
        try:
            conn = sqlite3.connect('test.db')

            while True:
                if not self.switchButton.isChecked():
                    break

                time.sleep(2)
                str11 = "SSR:" + str(round(random.uniform(90, 98), 2)) + "%"
                self.textBrowser.append(str11)
                self.textBrowser.moveCursor(self.textBrowser.textCursor().End)  # 移动光标到底部

            conn.close()
        except:
            pass

    def showVideoThread(self, isChecked=True):
        """
        调用本地摄像头按钮槽函数
        :param isChecked
        :return:
        """
        if isChecked:
            try:
                self.cap = cv2.VideoCapture(0)
                self.cameraTimer.start(100)
                self.cameraTimer.timeout.connect(self.OpenFrame)
                self.lb_video.setVisible(True)
            except:
                pass

        else:
            self.cap.release()
            self.cameraTimer.stop()
            self.lb_video.setVisible(False)

    @async_call
    def OpenFrame(self):
        """
        调用本地摄像头显示视频，同时是定时器的槽函数
        :return:
        """
        ret, image = self.cap.read()
        # 这个地方，与下面的地方放开后，打开摄像头看到的是实时的边缘检测视频
        # image = cv2.Canny(image, 50, 180)
        try:
            if ret:
                if self.frame_queue.full():
                    self.frame_queue.get()
                self.frame_queue.put(image)
                self.FrameConsumer()
            else:
                self.cap.release()
                self.cameraTimer.stop()
                print("视频打开失败")
            # self.capSave()  保存图片
            pass
        except:
            pass

    @async_call
    def FrameConsumer(self):
        while self.switchButton.isChecked():
            print('frame_queue size=', self.frame_queue.qsize())
            if self.frame_queue.qsize() > 0:
                frame = self.frame_queue.get_nowait()
                results = self.model.predict(source=frame, imgsz=3040)
                frame = results[0].plot()


                # resized_frame = cv2.resize(frame, (800, 600))
                # cv2.imshow("V8-SCAM", resized_frame)
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                video_img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
                self.lb_video.setPixmap(QPixmap(video_img))
                self.lb_video.setScaledContents(True)
                time.sleep(1)


    @async_call
    def capSave(self):
        FName = fr".\CapImages\cap{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
        # cv2.imwrite(FName + ".jpg", self.image)
        print(FName)
        # self.cap_label.setPixmap(QtGui.QPixmap.fromImage(self.showImage))
        self.video_img.save(FName + ".jpg", "JPG", 100)

    def setEnableStatus(self, isSwitchOn):
        """
        设置面板控件使能状态
        :param isSwitchOn: 开始采集开关闭合状态
        :return:
        """
        status = bool(1 - isSwitchOn)
        self.pb_settings.setEnabled(status)
        self.pb_export.setEnabled(status)

    def changeIcon(self, type=0, seed_index=0, switchOn=False):
        """
        改变控件icon槽函数
        :param type: 0 -> currentSeed, 1 -> cameraStatus
        :param seed_index: 0:pepper; 1:eggplant; 2:tomato
        :param switchOn: switch status
        :return:
        """
        if type == 0:
            if seed_index == 0:
                self.lb_currentSeed.setPixmap(QPixmap(":/pepper"))  # 在label上显示图片
            elif seed_index == 1:
                self.lb_currentSeed.setPixmap(QPixmap(":/eggplant"))  # 在label上显示图片
            elif seed_index == 2:
                self.lb_currentSeed.setPixmap(QPixmap(":/tomato"))  # 在label上显示图片

        if type == 1:
            picstr = r":/camera_on" if switchOn else r":/camera_off"
            self.lb_switchIcon.setPixmap(QtGui.QPixmap(picstr))

        # 让图片自适应label大小
        self.lb_switchIcon.setScaledContents(True)
        self.lb_currentSeed.setScaledContents(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainW = MainPageWindow()
    mainW.show()
    sys.exit(app.exec_())
