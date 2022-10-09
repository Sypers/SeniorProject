import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

class welcomescreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("welcomescreen.ui", self)
        self.show()
        self.livetrading.clicked.connect(self.gotolive)
        self.backtesting.clicked.connect(self.gototest)
        self.config.clicked.connect(self.gotoconfig)


    def gotolive(self):

        self.live = LiveTrading()
        self.live.show()
        self.close()
    def gotoconfig(self):
        self.config = configsettings()
        self.config.show()
        self.close()
    def gototest(self):
        self.test = backtesting()
        self.test.show()
        self.close()



class LiveTrading(QMainWindow):
    def __init__(self):
        super(LiveTrading, self).__init__()
        uic.loadUi("livetrading.ui",self)
        self.back.clicked.connect(self.gotoback)
        self.editstrategy.clicked.connect(self.gotoeditstra)


    def gotoback(self):
        self.welcome = welcomescreen()
        self.welcome.show()
        self.close()

    def gotoeditstra(self):
        self.editstr = EditStrategy()
        self.editstr.show()


class configsettings(QMainWindow):
    def __init__(self):
        super(configsettings,self).__init__()
        uic.loadUi("configsettings.ui",self)
        self.back.clicked.connect(self.gotoback)
        self.cryptopairs.clicked.connect(self.gotocrpytopairs)

    def gotoback(self):
        self.welcome = welcomescreen()
        self.welcome.show()
        self.close()
    def gotocrpytopairs(self):
        self.crypto = CryptoPairs()
        self.crypto.show()



class backtesting(QMainWindow):
    def __init__(self):
        super(backtesting,self).__init__()
        uic.loadUi("backtesting.ui",self)
        self.back.clicked.connect(self.gotoback)
        self.editstrategy.clicked.connect(self.gotoeditstra)
    def gotoback(self):
        self.welcome = welcomescreen()
        self.welcome.show()
        self.close()

    def gotoeditstra(self):
        self.editstr = EditStrategy()
        self.editstr.show()


class EditStrategy(QMainWindow):
    def __init__(self):
        super(EditStrategy, self).__init__()
        uic.loadUi("editstrategy.ui",self)
        self.back.clicked.connect(self.gotoback)
        self.save.clicked.connect(self.Fsave)

    def Fsave(self):
        self.close()
    def gotoback(self):
        self.close()
class CryptoPairs(QMainWindow):
    def __init__(self):
        super(CryptoPairs, self).__init__()
        uic.loadUi("cryptopairs.ui",self)
        self.save.clicked.connect(self.Fsave)


    def Fsave(self):
        self.close()



app = QApplication([])
window = welcomescreen()
app.exec_()




