import sys
import random
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time

from PyQt5.QtCore import Qt

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=2, height=5, dpi=70):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


# 设置默认颜色
# colors = ['#FD9048', '#F3ACBF', '#EBE5E1', '#84BAAF']  # #FF5733
# colors = ['#FFD700', '#F0F8FF', '#99CCCC', '#5F9EA0']
colors = ['#FFD700', '#D3D3D3', '#777E88', '#c06c84']

class CalResultsWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(CalResultsWindow, self).__init__(*args, **kwargs)
        self.initUI()

        self.canvas = MplCanvas(self, width=2, height=5, dpi=90)
        self.setCentralWidget(self.canvas)

        self.plug_tray_shape = [12, 6]     # 默认72盘

        # self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(lambda: self.update_plot(self.update_circles()))
        # self.timer.start()

    def initUI(self):
        # 设置窗口标志，移除右上角功能键
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)   # | Qt.FramelessWindowHint
        # 设置空图标，移除左上角图标
        self.setWindowIcon(QIcon())
        self.setFixedSize(140, 220)  #
        self.setWindowTitle('Call Results')

    def update_circles(self):
        # Drop off the first y element, append a new one.
        return [[1558, 2320], [442, random.randint(2000, 2989)], [1337, 2153], [425, 2300], [960, 547], [1442, random.randint(2000, 2989)]]

    def draw_plug(self, tray_size):
        if tray_size is not None:
            if tray_size == 72:
                self.plug_tray_shape = [12, 6]
            elif tray_size == 128:
                self.plug_tray_shape = [16, 8]
        self.canvas.axes.cla()  # Clear the canvas.

        # if colors is None:
        #     colors = default_colors1
        # else:
        #     for i in range(len(colors), 4):
        #         colors.append(default_colors[i])

        # 绘制棋盘格
        for i in range(self.plug_tray_shape[0] + 1):
            self.canvas.axes.axhline(i, color='#292321', lw=2)
        for j in range(self.plug_tray_shape[1] + 1):
            self.canvas.axes.axvline(j, color='#292321', lw=2)

        # 设置坐标轴范围
        self.canvas.axes.set_xlim(-0.03, self.plug_tray_shape[1] + 0.03)
        self.canvas.axes.set_ylim(-0.03, self.plug_tray_shape[0] + 0.05)

        # 隐藏坐标轴
        self.canvas.axes.set_xticks([])
        self.canvas.axes.set_yticks([])

    def update_plot(self, circle_coords, img_shape=[1570,3000], radius=12):
        """
        绘制棋盘格,圆点为黄色,空格子为红色,多个圆点的格子为蓝色,且圆点可见,并显示行列号居中于每个格子

        参数:
        circle_coords (list): 圆点坐标列表,例如 [[20, 30], [45, 60]]
        plug_shape (int): 穴盘规格
        radius (int): 圆点半径,默认为 15
        colors (list): 自定义颜色值列表,格式为 [圆点颜色, 空格子颜色, 单格颜色, 多圆点格子颜色]
        """
        # if plug_shape == 72:
        #     self.plug_tray_shape = [12, 6]
        # elif plug_shape == 128:
        #     self.plug_tray_shape = [16, 8]
        # self.canvas.axes.cla()  # Clear the canvas.
        #
        # if colors is None:
        #     colors = default_colors1
        # else:
        #     for i in range(len(colors), 4):
        #         colors.append(default_colors[i])
        #
        # # 创建画布
        # ax = self.canvas.axes
        #
        # # 绘制棋盘格
        # for i in range(self.plug_tray_shape[0] + 1):
        #     ax.axhline(i, color='#292321', lw=2)
        # for j in range(self.plug_tray_shape[1] + 1):
        #     ax.axvline(j, color='#292321', lw=2)
        #
        # # 设置坐标轴范围
        # ax.set_xlim(-0.03, self.plug_tray_shape[1] + 0.03)
        # ax.set_ylim(-0.03, self.plug_tray_shape[0] + 0.05)
        #
        # # 隐藏坐标轴
        # ax.set_xticks([])
        # ax.set_yticks([])

        # 取消注释实时刷新界面 TODO
        # self.draw_plug(self.plug_tray_shape[0]*self.plug_tray_shape[1])  # Clear the canvas.

        # 创建一个矩阵来记录每个格子内圆点的数量
        circle_matrix = np.zeros((self.plug_tray_shape[0], self.plug_tray_shape[1]), dtype=int)
        circle_coords_dict = {}
        num_record = [0, 0, 0]
        for x, y in circle_coords:
            x_cal, y_cal = x / img_shape[0] * self.plug_tray_shape[1], y / img_shape[1] * self.plug_tray_shape[0]
            row, col = int(y_cal), int(x_cal)
            circle_matrix[row, col] += 1
            circle = plt.Circle((x_cal, y_cal), radius / 100, color=colors[0], fill=True)
            self.canvas.axes.add_artist(circle)
            if (row, col) not in circle_coords_dict:
                circle_coords_dict[(row, col)] = [(x, y)]
            else:
                circle_coords_dict[(row, col)].append((x, y))

        # 绘制格子
        for i in range(self.plug_tray_shape[0]):
            for j in range(self.plug_tray_shape[1]):
                if circle_matrix[i, j] == 0:
                    num_record[0] += 1
                    rect = plt.Rectangle((j, i), 1, 1, color=colors[1], fill=True)
                    self.canvas.axes.add_artist(rect)
                elif circle_matrix[i, j] == 1:
                    num_record[1] += 1
                    rect = plt.Rectangle((j, i), 1, 1, color=colors[2], fill=True, zorder=0)
                    self.canvas.axes.add_artist(rect)
                    for x, y in circle_coords_dict[(i, j)]:
                        circle = plt.Circle((x / img_shape[0] * self.plug_tray_shape[1], y / img_shape[1] * self.plug_tray_shape[0]), radius / 100, color=colors[0], fill=True, zorder=1)
                        self.canvas.axes.add_artist(circle)
                elif circle_matrix[i, j] > 1:
                    num_record[2] += 1
                    rect = plt.Rectangle((j, i), 1, 1, color=colors[3], fill=True, zorder=0)
                    self.canvas.axes.add_artist(rect)
                    for x, y in circle_coords_dict[(i, j)]:
                        circle = plt.Circle((x / img_shape[0] * self.plug_tray_shape[1], y / img_shape[1] * self.plug_tray_shape[0]), radius / 100, color=colors[0], fill=True, zorder=1)
                        self.canvas.axes.add_artist(circle)

        # Trigger the canvas to update and redraw.
        self.canvas.draw()

        return num_record


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = CalResultsWindow()
    w.show()
    app.exec_()
