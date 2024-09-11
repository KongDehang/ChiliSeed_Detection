# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
import Resources.resources_rc
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from random import random, uniform

# ignore the "Sig..."
import warnings

from call_mainpage1 import MainPageWindow

warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainW = MainPageWindow(False)
    mainW.show()
    sys.exit(app.exec_())
