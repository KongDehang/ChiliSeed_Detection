import datetime
import os

from PyQt5 import QtCore, QtWidgets, QtGui
import sys

from PyQt5.QtWidgets import QAbstractItemView

import Resources.resources_rc

from PyQt5.QtGui import QIcon


##########################################
# ui界面设置
class Ui_ExportDialog(object):

    def setupUi(self, MainWindow):
        # 主窗口参数设置
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(450, 285)
        MainWindow.setWindowIcon(QIcon(':/export4'))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 设置展示已有数据文件控件QListView
        self.dataItemList = QtWidgets.QListWidget(self.centralwidget)
        self.dataItemList.setObjectName("dataItemList")
        self.dataItemList.setGeometry(QtCore.QRect(80, 20, 350, 130))
        self.dataItemList.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 按住CTRL可多选
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setWeight(50)
        self.dataItemList.setFont(font)
        # self.dataItemList.setText("数据文件：")

        # 设置按键参数
        self.file = QtWidgets.QPushButton(self.centralwidget)
        self.file.setGeometry(QtCore.QRect(400, 158, 30, 30))
        self.file.setObjectName("file")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/export1"))
        self.file.setIcon(icon)
        self.file.setIconSize(QtCore.QSize(30, 30))
        self.file.setStyleSheet(
            # "QPushButton{background-color:rgb(111,180,219)}"  # 按键背景色
            "QPushButton{background-color:transparent}"
            "QPushButton:hover{color:green}"  # 光标移动到上面后的前景色
            "QPushButton{border-radius:6px}"  # 圆角半径
            "QPushButton:pressed{background-color:rgb(180,180,180);border: None;}"  # 按下时的样式
        )

        # 设置路径显示textEdit
        self.pathText = QtWidgets.QLineEdit(self.centralwidget)
        self.pathText.setObjectName("pathText")
        self.pathText.setGeometry(QtCore.QRect(80, 160, 350, 28))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(50)
        self.pathText.setFont(font)
        self.pathText.setText(os.path.join(os.path.expanduser("~"), 'Desktop'))

        # 设置文件名字
        self.filenameText = QtWidgets.QLineEdit(self.centralwidget)
        self.filenameText.setObjectName("filenameText")
        self.filenameText.setGeometry(QtCore.QRect(80, 195, 350, 28))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(50)
        self.filenameText.setFont(font)
        self.filenameText.setText("result" + datetime.datetime.now().strftime('%Y-%m-%d'))

        # 设置路径和文件名title
        self.dataItemListLabel = QtWidgets.QLabel(self.centralwidget)
        self.dataItemListLabel.setObjectName("dataItemListLabel")
        self.dataItemListLabel.setGeometry(QtCore.QRect(15, 20, 100, 30))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setWeight(50)
        self.dataItemListLabel.setFont(font)
        self.dataItemListLabel.setText("数据文件：")

        self.pathTextLabel = QtWidgets.QLabel(self.centralwidget)
        self.pathTextLabel.setObjectName("pathTextLabel")
        self.pathTextLabel.setGeometry(QtCore.QRect(15, 160, 100, 30))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setWeight(50)
        self.pathTextLabel.setFont(font)
        self.pathTextLabel.setText("存储路径：")

        self.filenameTextLabel = QtWidgets.QLabel(self.centralwidget)
        self.filenameTextLabel.setObjectName("filenameTextLabel")
        self.filenameTextLabel.setGeometry(QtCore.QRect(15, 195, 100, 30))
        font = QtGui.QFont()
        font.setFamily("等线")
        font.setPointSize(10)
        font.setWeight(50)
        self.filenameTextLabel.setFont(font)
        self.filenameTextLabel.setText("文件名称：")

        # 设置按键参数
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(240, 235, 80, 25))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setText("保存")

        self.cancleButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancleButton.setGeometry(QtCore.QRect(350, 235, 80, 25))
        self.cancleButton.setObjectName("cancleButton")
        self.cancleButton.setText("取消")

        # 主窗口及菜单栏标题栏设置
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 350, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        ################button按钮点击事件回调函数################

        self.file.clicked.connect(self.msg)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "导出数据"))
        self.file.raise_()

    # 选择路径文件夹***********************************
    def msg(self, Filepath):
        m = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", "C:/")  # 起始路径
        self.pathText.setText(m)


#########主函数入口 #########

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    mainWindow = QtWidgets.QMainWindow()

    ui = Ui_ExportDialog()

    ui.setupUi(mainWindow)

    mainWindow.show()

    sys.exit(app.exec_())

