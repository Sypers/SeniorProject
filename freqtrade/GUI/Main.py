import json
import os
import sys
from pathlib import Path

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *


class welcomescreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("welcomescreen.ui", self)
        self.live = None
        self.test = None
        self.config1 = None
        self.show()
        self.livetrading.clicked.connect(self.gotolive)
        self.backtesting.clicked.connect(self.gototest)
        self.config.clicked.connect(self.gotoconfig)

    def gotolive(self):
        if self.live is None:
            self.live = LiveTrading()
            self.live.show()
        else:
            self.live.show()

    def gotoconfig(self):
        if self.config1 is None:
            self.config1 = configsettings()
            self.config1.show()
        else:
            self.config1.show()

    def gototest(self):
        if self.test is None:
            self.test = backtesting()
            self.test.show()
        else:
            self.test.show()


class LiveTrading(QMainWindow):
    def __init__(self):
        super(LiveTrading, self).__init__()
        uic.loadUi("livetrading.ui", self)
        self.back.clicked.connect(self.gotoback)
        self.editstrategy.clicked.connect(self.gotoeditstra)

    def gotoback(self):
        window.show()
        self.close()

    def gotoeditstra(self):
        self.editstr = EditStrategy()
        self.editstr.show()


class configsettings(QMainWindow):
    def __init__(self):
        super(configsettings, self).__init__()
        uic.loadUi("configsettings.ui", self)
        self.ComboCurr()
        self.save.clicked.connect(self.gotosave)
        self.back.clicked.connect(self.gotoback)
        self.cryptopairs.clicked.connect(self.gotocrpytopairs)
        self.checkBox.clicked.connect(self.checkEnab)

    def ComboCurr(self):
        assestList = ["USDT", "BTC", "ETH", "XRP", "LTC", "BCH"]
        for i in assestList:
            self.comboBox.addItem(i)

    def checkEnab(self):
        if self.checkBox.isChecked():
            self.lineEdit_5.setEnabled(True)
        else:
            self.lineEdit_5.setEnabled(False)

    def gotosave(self):
        try:
            self.Max_Open_Trades = int(self.lineEdit.text())
            self.Stake_Amount = int(self.lineEdit_2.text())
            self.Wallet_Amount = int(self.lineEdit_4.text())
            self.DisplayCurrency = self.lineEdit_3.text()
            self.platformKey = self.lineEdit_6.text()
            self.platformSecret = self.lineEdit_7.text()
            if self.checkBox.isChecked():
                self.DryWallet = int(self.lineEdit_5.text())
            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "config.json"
            print(my_path)
            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                data["max_open_trades"] = self.Max_Open_Trades
                data["stake_amount"] = self.Stake_Amount
                data["fiat_display_currency"] = self.DisplayCurrency
                data["exchange"]["key"] = self.platformKey
                data["exchange"]["secret"] = self.platformSecret
                data["dry_run_wallet"] = self.Wallet_Amount
            with open(my_path, "w") as jsonFile:
                json.dump(data, jsonFile, indent=2)

        except ValueError:
            self.errorL.setText("Max Open Trades, Stake Amount, Wallet Amount, Dry-run Wallet must be numbers ")

    # def saveFunction(MOT, SA, WA, DC, PFK, PFS, DW=None):
    #     print("i am here")

    def gotoback(self):
        window.show()
        self.close()

    def gotocrpytopairs(self):
        self.crypto = CryptoPairs()
        self.crypto.show()


class backtesting(QMainWindow):
    def __init__(self):
        super(backtesting, self).__init__()
        uic.loadUi("backtesting.ui", self)
        self.back.clicked.connect(self.gotoback)
        self.editstrategy.clicked.connect(self.gotoeditstra)

    def gotoback(self):
        window.show()
        self.close()

    def gotoeditstra(self):
        self.editstr = EditStrategy()
        self.editstr.show()


class EditStrategy(QMainWindow):
    def __init__(self):
        super(EditStrategy, self).__init__()
        uic.loadUi("editstrategy.ui", self)
        self.back.clicked.connect(self.gotoback)
        self.save.clicked.connect(self.Fsave)

    def Fsave(self):
        self.close()

    def gotoback(self):
        self.close()


class CryptoPairs(QMainWindow):
    def __init__(self):
        super(CryptoPairs, self).__init__()
        uic.loadUi("cryptopairs.ui", self)
        self.save.clicked.connect(self.Fsave)

    def Fsave(self):
        self.close()


def main():
    app = QApplication([])
    global window
    window = welcomescreen()
    app.exec_()


if __name__ == '__main__':
    main()
