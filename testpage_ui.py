import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt

class SubWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.label = QLabel('Random Number: ')
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_number)
        self.timer.start(1000)  # Update every 1 second

    def update_number(self):
        random_number = random.randint(1, 100)
        self.label.setText(f'Random Number: {random_number}')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('Collapsible Sub-Window Example')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.toggle_button = QPushButton('Show/Hide Sub-Window', self)
        self.toggle_button.clicked.connect(self.toggle_sub_window)
        self.layout.addWidget(self.toggle_button)

        self.sub_window = SubWindow()
        self.sub_window.hide()
        self.layout.addWidget(self.sub_window)

        self.layout.addStretch(1)

    def toggle_sub_window(self):
        if self.sub_window.isVisible():
            self.sub_window.hide()
        else:
            self.sub_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
