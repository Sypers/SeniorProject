import json
import os
import sys
from pathlib import Path

import binance.exceptions
from binance.client import Client
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *


# ---------Login Window------------------------------------------------------------------


class loginWindow(QMainWindow):
    def __init__(self):
        super(loginWindow, self).__init__()
        uic.loadUi("login.ui", self)
        self.show()
        self.loginb.clicked.connect(self.gotologin)
        self.skipb.clicked.connect(self.skipbb)

    def skipbb(self):
        api_key = 'y3FaQ51hj5LSxABpVoBBT192GluNy4wTtYXmpylPNzJauM4kwYvOqXlM09LCjiYt'
        api_secret = 'X5HWDbk4ugsmH0v2sk1b6ytqKiNxxBDqnCunzwKbv2DNvuh94PzzgSJ4voX6LNgD'
        global checkapi
        checkapi = Client(api_key, api_secret)

        global window
        window = welcomescreen()
        self.close()

    def gotologin(self):
        try:
            self.platformKey = self.apikey.text()
            self.platformSecret = self.apisecret.text()

            # Check if API key and Secret are Correct or not
            global checkapi
            checkapi = Client(self.platformKey, self.platformSecret)
            bal = checkapi.get_account()

            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "config.json"
            print(my_path)

            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                data["exchange"]["key"] = self.platformKey
                data["exchange"]["secret"] = self.platformSecret
            with open(my_path, "w") as jsonFile:
                json.dump(data, jsonFile, indent=2)

            global window
            window = welcomescreen()
            self.close()



        except binance.exceptions.BinanceAPIException:
            self.errorL.setText("invalid API_key or APi_Secret")


# -------------- Welcome Screen window------------------------------------------------


class welcomescreen(QMainWindow):
    def __init__(self):
        super(welcomescreen, self).__init__()
        uic.loadUi("welcomescreen.ui", self)
        self.live = None
        self.test = None
        self.config1 = None
        self.customize = None
        self.show()
        self.livetrading.clicked.connect(self.gotolive)
        self.backtesting.clicked.connect(self.gototest)
        self.config.clicked.connect(self.gotoconfig)
        self.cust.clicked.connect(self.gotoCustomizeStrategy)

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

    def gotoCustomizeStrategy(self):
        if self.customize is None:
            self.customize = EditStrategy()
            self.customize.show()
        else:
            self.customize.show()


# ----------Live Trading Window-------------------------------------------------------------


class LiveTrading(QMainWindow):
    def __init__(self):
        super(LiveTrading, self).__init__()
        uic.loadUi("livetrading.ui", self)
        self.editstr = None
        self.back.clicked.connect(self.gotoback)

    def gotoback(self):
        window.show()
        self.close()

# -------------Config Window----------------------------------------------------------------


class configsettings(QMainWindow):
    def __init__(self):
        super(configsettings, self).__init__()
        uic.loadUi("configsettings.ui", self)
        self.crypto = None
        self.ComboCurr()
        self.save.clicked.connect(self.gotosave)
        self.back.clicked.connect(self.gotoback)
        self.cryptopairs.clicked.connect(self.gotocrpytopairs)
        self.checkBox.clicked.connect(self.checkEnab)

    def ComboCurr(self):
        assestList = ["USDT", "BTC", "ETH", "XRP", "LTC", "BCH"]
        for i in assestList:
            self.stakecombo.addItem(i)

    def checkEnab(self):
        if self.checkBox.isChecked():
            self.lineEdit_5.setEnabled(True)
        else:
            self.lineEdit_5.setEnabled(False)

    def gotosave(self):
        try:
            self.errorL.setText("")
            self.Max_Open_Trades = int(self.lineEdit.text())
            self.Stake_Amount = int(self.lineEdit_2.text())
            self.Wallet_Amount = int(self.lineEdit_4.text())
            self.DisplayCurrency = self.lineEdit_3.text()
            self.stakeStr = self.stakecombo.currentText()

            if self.checkBox.isChecked():
                self.DryWallet = int(self.lineEdit_5.text())

            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "config.json"
            print(my_path)
            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                data["stake_currency"] = self.stakeStr
                data["max_open_trades"] = self.Max_Open_Trades
                data["stake_amount"] = self.Stake_Amount
                data["fiat_display_currency"] = self.DisplayCurrency
                data["dry_run_wallet"] = self.Wallet_Amount
            with open(my_path, "w") as jsonFile:
                json.dump(data, jsonFile, indent=2)

            self.errorL.setText("successfully connected to Binance Platform, And Saved all the information above ")

        except ValueError:
            self.errorL.setText("Max Open Trades, Stake Amount, Wallet Amount, Dry-run Wallet must be numbers ")

    def gotoback(self):
        window.show()
        self.close()

    def gotocrpytopairs(self):
        # if self.crypto is None:
        self.crypto = CryptoPairs()
        self.crypto.show()
        # else:
        #     self.crypto.show()


# ----------------backtest interface -----------------------------------------------------------------------------------


class backtesting(QMainWindow):

    def __init__(self):
        super(backtesting, self).__init__()
        uic.loadUi("backtesting.ui", self)
        self.back.clicked.connect(self.gotoback)


    def gotoback(self):
        window.show()
        self.close()




class EditStrategy(QMainWindow):

    def __init__(self):
        super(EditStrategy, self).__init__()
        uic.loadUi("editstrategy.ui", self)
        # self.combostr = QComboBox()
        # self.hroi = QLineEdit

        # self.listroi = QListWidget()
        self.comboload()
        self.loadinformation()
        self.appendroi.clicked.connect(self.appendbutton)
        self.back.clicked.connect(self.gotoback)
        self.save.clicked.connect(self.Fsave)

    def comboload(self):
        root_folder = Path(__file__).parents[2]
        my_path = root_folder / "user_data" / "strategies"

        print(os.listdir(my_path))
        for i in os.listdir(my_path):
            if i.endswith(".json"):
                self.combostr.addItem(i)

    def loadinformation(self):
        self.listroi.clear()
        root_folder = Path(__file__).parents[2]
        global currentSelect
        currentSelect = self.combostr.currentText()
        my_path = root_folder / "user_data" / "strategies" / self.combostr.currentText()
        print(my_path)
        with open(my_path, 'r') as jsonFile:
            data = json.load(jsonFile)
            RoiList = data["params"]["roi"]
        for i in RoiList:
            result = i + ":" + str(RoiList[i] * 100)
            self.listroi.addItem(result)
        self.hroi.setText(str((RoiList["0"] * 100)))
        print(self.hroi.text())
        currValue = 0
        for i in RoiList:
            if eval(i) > currValue:
                currValue = eval(i)
        self.mroi.setText(str(currValue))

        # -----roi Done--------------------------------------------------

    def appendbutton(self):
        try:
            global Rlist
            Rlist = {}

            durationValue = eval(self.droi.text())
            percValue = float(eval(self.proi.text()))
            highestroi = eval(self.hroi.text())
            maxduration = eval(self.mroi.text())
            if durationValue == 0 or durationValue is None and percValue == 0 or percValue is None:
                raise NoValueError
            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "user_data" / "strategies" / self.combostr.currentText()
            print(my_path)
            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                RoiList = data["params"]["roi"]
                Rlist = data["params"]["roi"]
            # Max Duration
            MaxDura = 0
            for i in RoiList:
                if eval(i) > MaxDura:
                    MaxDura = eval(i)
            # Max Percentage
            MaxPerc = 0
            for i in RoiList:
                if RoiList[i] > MaxPerc:
                    MaxPerc = RoiList[i]

            # check for if highest Roi is less than any other percentage
            for i in RoiList:
                if RoiList[i] > (highestroi / 100):
                    raise MaxPercIsLessThanPercs
            # add new Highest ROI
            if MaxPerc == (highestroi / 100):
                pass
            else:
                # self.listroi.takeItem(0)
                # highest = "0:" + str(highestroi)
                # self.listroi.addItem(highest)
                Rlist["0"] = (highestroi / 100)
            # Check duration
            for i in RoiList:
                if eval(i) > maxduration:
                    raise MaxDurationIsNotMax
            if MaxDura == durationValue:
                pass
            else:
                print(type(MaxDura))
                print(MaxDura)
                Rlist.pop(str(MaxDura))
                Rlist[str(maxduration)] = 0
            # check for ROI and Duration Append
            for i in RoiList:

                if eval(i) < durationValue:

                    if RoiList[i] > (percValue / 100):
                        pass
                    else:
                        raise percentageError
                else:
                    pass
            # Check if there is Same Duration
            for i in RoiList:
                if eval(i) == durationValue:
                    raise SameDuration
            # Check if There is same percentage

            for i in RoiList:
                if RoiList[i] == (percValue / 100):
                    raise SamePerc
            # check if the duration is bigger than max duration
            if durationValue > MaxDura:
                raise DurationHigherThanMax
            # check if the percentage is bigger than max percentage
            if (percValue / 100) > MaxPerc:
                raise percHigherThanMax

            # add max Roi to the list
            Rlist[str(durationValue)] = (percValue / 100)
            # sort Dict
            Rlist = sorted(Rlist.items(), key=lambda x: x[1], reverse=True)
            Rlist = dict(Rlist)
            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "user_data" / "strategies" / currentSelect
            print(my_path)
            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                data["params"]["roi"] = Rlist
            with open(my_path, "w") as jsonFile:
                json.dump(data, jsonFile, indent=2)
            self.errorR.setText("")
            self.loadinformation()


        except ValueError:
            self.errorR.setText("Please insert Value in Duration and (%)")
        except DurationHigherThanMax:
            self.errorR.setText("Duration Value is Higher than Max Duration!!")
        except percHigherThanMax:
            self.errorR.setText("percentage Value is Higher than ROI max!!")
        except percentageError:
            self.errorR.setText("Wrong percentage and duration you must follow the order!")
        except MaxPercIsLessThanPercs:
            self.errorR.setText("ROI Max is less than percentages in List")
        except NoValueError:
            self.errorR.setText("Please insert Value in Duration and (%)")
        except SamePerc:
            self.errorR.setText("There is already Same Percentage")
        except SameDuration:
            self.errorR.setText("There is already Same Duration")
        except MaxDurationIsNotMax:
            self.errorR.setText("Max Duration is Not the Highest")

    def deleteb(self):
        pass

    def Fsave(self):
        self.close()

    def gotoback(self):
        window.show()
        self.close()


# ----------Crypto window --------------------------------------------------------------


class CryptoPairs(QMainWindow):

    def __init__(self):
        super(CryptoPairs, self).__init__()
        uic.loadUi("cryptopairs.ui", self)
        # self.selectedpairs = QListWidget()
        # self.availablepairs = QListWidget()
        self.loadInformation()
        self.save.clicked.connect(self.Fsave)
        self.insertb.clicked.connect(self.insertItemsToSP)
        self.deleteb.clicked.connect(self.deleteItemsToAP)

    def loadInformation(self):
        root_folder = Path(__file__).parents[2]
        my_path1 = root_folder / 'config.json'
        print(my_path1)
        with open(my_path1, 'r') as jsonFile:
            data = json.load(jsonFile)
            self.stakeString = data["stake_currency"]

        exchange_info = checkapi.get_exchange_info()

        for i in exchange_info['symbols']:
            # print(i['quoteAsset'])
            if i['quoteAsset'] == self.stakeString:
                itemsstr = i['baseAsset'] + "/" + i['quoteAsset']
                # print(itemsstr)
                self.availablepairs.addItem(itemsstr)

                # print(i['baseAsset'] + " Asset : " + i['quoteAsset'])

        self.availablepairs.sortItems()

    def insertItemsToSP(self):
        isitem = self.availablepairs.selectedItems()
        if not isitem:
            print("nothing to add")
            return
        print(self.availablepairs.currentItem().text())

        row = self.availablepairs.currentRow()
        self.selectedpairs.addItem(self.availablepairs.takeItem(row))
        # self.availablepairs.currentItem()

    def deleteItemsToAP(self):
        isitem = self.selectedpairs.selectedItems()
        if not isitem:
            print('nothing to delete')
            return
        print(self.selectedpairs.currentItem().text())

        row = self.selectedpairs.currentRow()
        self.availablepairs.addItem(self.selectedpairs.takeItem(row))

    def Fsave(self):
        items = []
        for x in range(self.selectedpairs.count()):
            items.append(self.selectedpairs.item(x).text())

        root_folder = Path(__file__).parents[2]
        my_path = root_folder / "config.json"
        print(my_path)

        with open(my_path, 'r') as jsonFile:
            data = json.load(jsonFile)
            data["exchange"]["pair_whitelist"] = items
        with open(my_path, "w") as jsonFile:
            json.dump(data, jsonFile, indent=2)

        print(items)
        self.close()


# ----------Welcome First Time window----------------------------------------------------


class welcomepage(QMainWindow):
    def __init__(self):
        super(welcomepage, self).__init__()
        uic.loadUi('welcomepage.ui', self)
        self.show()
        self.nextb.clicked.connect(self.goNext)

    def goNext(self):
        self.helpg = helpguide()
        self.helpg.show()
        self.close()


# -----------help Guide First Time Window---------------------------------------------------


class helpguide(QMainWindow):
    def __init__(self):
        super(helpguide, self).__init__()
        uic.loadUi('help.ui', self)
        self.nextb.clicked.connect(self.goNext)

    def goNext(self):
        with open('readme.txt', 'x') as f:
            f.write('Create a new text file!')

        self.loginwindow = loginWindow()

        self.close()


# ----------Exceptions handler---------------------------------------------------------------


class Error(Exception):
    pass


class SameDuration(Error):
    pass


class SamePerc(Error):
    pass


class DurationHigherThanMax(Error):
    pass


class MaxDurationIsNotMax(Error):
    pass


class percHigherThanMax(Error):
    pass


class percentageError(Error):
    pass


class NoValueError(Error):
    pass


class MaxPercIsLessThanPercs(Error):
    pass


# ----------Main-----------------------------------------------------------------------------
def main():
    root_folder = Path(__file__).parents[0]
    my_path = root_folder / "readme.txt"
    isExists = os.path.exists(my_path)
    print(root_folder)
    print(my_path)
    print(isExists)
    if not isExists:
        app = QApplication([])
        welcome = welcomepage()
        app.exec_()
    else:
        app = QApplication([])
        loginwindow = loginWindow()
        app.exec_()


if __name__ == '__main__':
    main()
