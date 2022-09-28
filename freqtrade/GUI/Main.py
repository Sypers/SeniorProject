import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

class welcomescreen(QMainWindow):
    def __init__(self):
        super(welcomescreen, self).__init__()
        uic.loadUi("welcomescreen.ui", self)

        self.show()

def main():

    app = QApplication([])
    window = welcomescreen()
    app.exec_()




