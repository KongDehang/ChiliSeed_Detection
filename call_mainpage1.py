import copy
import sys
import random
import sqlite3
import sys
import threading
import time
from queue import Queue

import cv2
import torch
import zmq
import base64
import numpy as np
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtWidgets import *

import Components.QSwitchButton
from Components.show_plate_calresults import CalResultsWindow
from HomePages.mainpage_ui import Ui_MainWindow
from Scripts import json_unit, sqlite_unit
from call_exportpage import ExportPage
from call_settingspage import SettingsWindow
from ultralytics import YOLO
from concurrent.futures import ThreadPoolExecutor, as_completed

lock = threading.Lock()
frame_queue = Queue(maxsize=1)
frame_processed = None
global_data_array = np.array([[1,1,1], [2,2,2]])
before_data_array = np.array([[1,1,1], [2,2,2]])
# 初始化 ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://172.20.49.47:5555")
socket.subscribe("")

# ignore the "Sig..."
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class VideoThread(threading.Thread):
    """
    采集图片，补充图片序列
    """

    def __init__(self, using_camera=True, video_path=None):
        threading.Thread.__init__(self)
        self.video_path = video_path
        self.using_camera = using_camera
        self.stop_flag = threading.Event()

    def run(self):
        if not self.using_camera and self.video_path is None:
            print("Please specify a video path")

        # 使用视频或相机实时采集
        cap = cv2.VideoCapture(0) if self.using_camera else cv2.VideoCapture(self.video_path)
        print('Start video thread')

        while not self.stop_flag.is_set():
            ret, image = cap.read()
            # print('get frame = ', ret)
            if not ret:
                break
            # lock.acquire()
            if frame_queue.full():    # ToDo 采用传感器抽取关键帧时注意变化
                frame_queue.get()
            frame_queue.put(image)
            # lock.release()

            time.sleep(0.01)  # 控制帧率
        cap.release()

    def stop(self):
        self.stop_flag.set()


class ModelThread(threading.Thread):
    """
    消耗图片，进行检测
    """
    def __init__(self, using_camera=True):
        threading.Thread.__init__(self)
        self.model = YOLO(r'..\weights\best.pt').to('cuda' if torch.cuda.is_available() else 'cpu')
        self.using_camera = using_camera
        self.stop_flag = threading.Event()

        self.pool = ThreadPoolExecutor(max_workers=4)  # 线程池

    def run(self):
        global frame_processed
        global global_data_array
        print('Start model thread')

        while not self.stop_flag.is_set():
            try:
                # print('Frame_queue size=', frame_queue.qsize())
                if frame_queue.qsize() > 0:
                    if self.using_camera:
                        # 实时检测方式（取消注释）
                        frame = frame_queue.get_nowait()
                        results = self.model.predict(source=frame, imgsz=3040)

                        # 存储检测结果给全局变量,前两列为（x, y）
                        if results[0].boxes.shape[0] > 0:
                            global_data_array = results[0].boxes.xywh.cpu().numpy()[:, :2]
                            # global_data_array = np.round(results[0].boxes.xywh.cpu().numpy()[:, :2], 2)
                            # print(global_data_array)

                        lock.acquire()
                        frame_processed = results[0].plot()
                        lock.release()

                    else:
                        # lock.acquire()
                        frame = frame_queue.get_nowait()
                        # 裁剪并进行推理
                        cropped_frame = frame[0:3000, 1275:2875]
                        results = self.model.predict(source=cropped_frame, imgsz=3040)

                        # 存储检测结果给全局变量,前两列为（x, y）
                        if results[0].boxes.shape[0] > 0:
                            global_data_array = results[0].boxes.xywh.cpu().numpy()[:, :2]
                            # global_data_array = np.round(results[0].boxes.xywh.cpu().numpy()[:, :2], 2)
                            # print(global_data_array)

                        # 可视化结果
                        frame[0:3000, 1275:2875] = results[0].plot()

                        lock.acquire()
                        frame_processed = frame
                        lock.release()

                else:
                    time.sleep(0.1)

            except Exception as e:
                print(f"model thread error{e}")

    def stop(self):
        self.stop_flag.set()


class MainPageWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    chooseSignal = pyqtSignal(str)
    global frame_queue
    global frame_processed

    def __init__(self, using_camera=True, parent=None):
        super(MainPageWindow, self).__init__(parent)

        # 初始化窗口
        self.setupUi(self)
        self.setWindowIcon(QIcon(':/seed'))
        # self.cameraTimer = QTimer()
        self.switchButton = Components.QSwitchButton.SwitchButton(parent=self)
        self.settingsWindow = SettingsWindow()
        self.exportDialog = ExportPage()
        self.calResultsDialog = CalResultsWindow()
        self.using_camera = using_camera

        # 初始化目标检测模型
        self.model = YOLO(r'..\weights\best.pt').to('cuda' if torch.cuda.is_available() else 'cpu')

        # 初始化线程
        self.video_thread = None
        self.model_thread = None
        self.pool = ThreadPoolExecutor(max_workers=6)  # 线程池

        # 事件建立响应
        self.initUI()

    def initUI(self):

        # self.pushButton.clicked.connect(lambda: self.textEdit.clear())
        self.pb_export.clicked.connect(self.exportData)
        self.pb_settings.clicked.connect(self.showSettingsWindow)
        self.pb_showcalcavs.clicked.connect(self.show_plate_cal_results)
        self.switchButton.switch_toggled.connect(self.switchChanged)
        self.switchButton.move(15, 68)
        self.update()

    def update(self):
        try:
            # 初始化数据库
            conn = sqlite3.connect('test.db')
            sqlite_unit.create_table(conn)
            conn.close()
            print("Ready!")
        except:
            print("Database creation failed!")
            pass

        last_settings = json_unit.json_read(r"./Config/settings.json")
        self.changeIcon(0, seed_index=int(last_settings["selected_seed"]))
        self.calResultsDialog.draw_plug(tray_size=int(last_settings["tray_size"]))

        # ToDo 参数设置窗口设置后的参数更新；采集间隔等……

    def exportData(self):
        self.exportDialog.setWindowModality(Qt.ApplicationModal)
        self.exportDialog.show()

    def showSettingsWindow(self):
        self.settingsWindow.setWindowModality(Qt.ApplicationModal)
        self.settingsWindow.chooseSignal.connect(self.update)
        self.settingsWindow.updateSettings()
        self.settingsWindow.show()

    def show_plate_cal_results(self):
        if self.calResultsDialog.isVisible():
            time.sleep(0.1)
            # self.calResultsDialog.hide()
            self.calResultsDialog.setHidden(True)
        else:
            time.sleep(0.1)
            # self.calResultsDialog.show()
            self.calResultsDialog.setHidden(False)

    def switchChanged(self):
        """ 开关按钮选中状态改变的槽函数 """
        isChecked = self.switchButton.isChecked()

        self.setEnableStatus(isChecked)  # 设置面板控件是使能状态
        self.changeIcon(1, switchOn=isChecked)  # 改变开关按钮图标

        if isChecked:
            self.start()
        else:
            self.stop()

    def start(self):
        try:
            self.calResultsDialog.draw_plug(
                tray_size=72 if self.settingsWindow.traysize_CB.currentIndex() == 0 else 128)
            self.lb_video.setVisible(True)  # 保证每一次开启与关断创建新的线程，重新start不会发生错误
            if self.using_camera:
                # 使用相机采集视频检测
                self.video_thread = VideoThread()
                self.video_thread.daemon = True

                self.model_thread = ModelThread()
                self.model_thread.daemon = True
            else:
                # 使用录像视频检测
                self.video_thread = VideoThread(False, video_path=r"E:\ADataset\datasets\videosets\z600.mp4")
                self.video_thread.daemon = True
                self.model_thread = ModelThread(False)
                self.model_thread.daemon = True

            self.model_thread.start()
            time.sleep(0.5)
            self.video_thread.start()
            self.pool.submit(self.mainLoop, 1)

        except Exception as e:
            self.lb_video.setVisible(False)
            print(f"start thread error{e}")

    def stop(self):
        self.lb_video.setVisible(False)
        self.calResultsDialog.close()
        self.video_thread.stop()
        self.model_thread.stop()

        self.video_thread.join(timeout=0.1)
        self.model_thread.join(timeout=0.1)

    def mainLoop(self, n):
        try:
            while self.video_thread.is_alive():
                time.sleep(0.001)
                # as_completed(self.pool.submit(self.UpdateThread, 2))
                self.pool.submit(self.UpdateThread, 2)
                self.pool.submit(self.frameRefresh, 4)
                # as_completed(self.pool.submit(self.frameRefresh, 4))

        except Exception as e:
            print("text update thread stopped !!! : " + f"{e}")
            self.calResultsDialog.close()
            self.stop()

    def UpdateThread(self, n):
        global global_data_array
        global before_data_array
        conn = sqlite3.connect('test.db')
        try:
            if not np.array_equal(before_data_array, global_data_array):
                before_data_array = copy.deepcopy(global_data_array)  # 深拷贝
                # 获取检测盘序号
                plug_tray_nm = sqlite_unit.get_max_data(conn, 0, "Plugtray_Number") + 1
                # 插入1列
                new_column = np.full((global_data_array.shape[0], 1), plug_tray_nm)
                new_matrix = np.hstack((new_column, global_data_array))

                # 坐标数据写入数据库
                sqlite_unit.insert_data(conn, new_matrix, 0, True)

                # 显示和计算单粒率
                plug_shape = 72 if self.settingsWindow.traysize_CB.currentIndex() == 0 else 128
                srm_count = self.calResultsDialog.update_plot(global_data_array)
                ssr = round(srm_count[1] / plug_shape * 100, 2)
                rsr = round(srm_count[2] / plug_shape * 100, 2)
                msr = round(100-ssr-rsr, 2)
                sqlite_unit.insert_data(conn, [plug_tray_nm, ssr, rsr, msr, global_data_array.shape[0], round(random.uniform(48, 62), 1)], 1)

                # 更新text browser显示
                str_for_update = "S:" + f"{ssr}%" + "|" + "R:" + f"{rsr}%" + "|" + "M:" + f"{msr}%"
                self.textBrowser.append(str_for_update)
                self.textBrowser.moveCursor(self.textBrowser.textCursor().End)  # 移动光标到底

            # 更新界面数据
            datas = sqlite_unit.get_ave_values(conn)  # 数据均值计算
            if len(datas) > 0:
                self.lb_number_dn.setText(str(datas[0]))
                self.lb_number_asr.setText(str(datas[1]) + "%")
                self.lb_number_arr.setText(str(datas[2]) + "%")
                self.lb_number_amr.setText(str(datas[3]) + "%")


        except Exception as e:
            print(e)
        conn.close()

    def frameRefresh(self, n):
        """实时刷新画面"""
        lock.acquire()
        if frame_processed is not None:
            image = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2RGB)
            video_img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
            self.lb_video.setPixmap(QPixmap(video_img))
            self.lb_video.setScaledContents(True)
        lock.release()

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
    mainwindow = MainPageWindow(False)   # True相机实时检测;False检测视频
    mainwindow.show()
    sys.exit(app.exec_())
