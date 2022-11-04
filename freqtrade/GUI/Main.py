import json
import os
import signal
import socket
import sys
from pathlib import Path
import subprocess
import threading
import binance.exceptions
import requests.exceptions
import urllib3.exceptions
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
        self.loginb.clicked.connect(self.skipbb)

    def skipbb(self):
        try:
            api_key = 'y3FaQ51hj5LSxABpVoBBT192GluNy4wTtYXmpylPNzJauM4kwYvOqXlM09LCjiYt'
            api_secret = 'X5HWDbk4ugsmH0v2sk1b6ytqKiNxxBDqnCunzwKbv2DNvuh94PzzgSJ4voX6LNgD'
            global ClientAPIConn
            ClientAPIConn = Client(api_key, api_secret)
            global window
            window = welcomescreen()
            self.close()
        except binance.exceptions.BinanceAPIException:
            self.errorL.setText("invalid API_key or APi_Secret")
        except urllib3.exceptions.NewConnectionError:
            self.errorL.setText("Connection Error")
        except requests.exceptions.ConnectionError:
            self.errorL.setText("Connection Error")
        except urllib3.exceptions.MaxRetryError:
            self.errorL.setText("Connection Error")
        except ConnectionError:
            self.errorL.setText("Connection Error")

    def gotologin(self):
        try:
            self.platformKey = self.apikey.text()
            self.platformSecret = self.apisecret.text()

            # Check if API key and Secret are Correct or not
            global ClientAPIConn
            ClientAPIConn = Client(self.platformKey, self.platformSecret)
            bal = ClientAPIConn.get_account()

            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "config.json"


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
        except socket.gaierror:
            self.errorL.setText("Connection Error")

        except urllib3.exceptions.NewConnectionError:
            self.errorL.setText("Connection Error")
        except requests.exceptions.ConnectionError:
            self.errorL.setText("Connection Error")
        except urllib3.exceptions.MaxRetryError:
            self.errorL.setText("Connection Error")
        except ConnectionError:
            self.errorL.setText("Connection Error")


# -------------- Welcome Screen window------------------------------------------------


class welcomescreen(QMainWindow):
    def __init__(self):
        super(welcomescreen, self).__init__()
        uic.loadUi("welcomescreen.ui", self)
        self.live = None
        self.test = None
        self.config1 = None
        self.customize = None
        self.instructions1 = None
        self.aboutus1 = None
        self.show()
        self.livetrading.clicked.connect(self.gotolive)
        self.backtesting.clicked.connect(self.gototest)
        self.config.clicked.connect(self.gotoconfig)
        self.cust.clicked.connect(self.gotoCustomizeStrategy)
        self.aboutus.clicked.connect(self.gotoaboutus)
        self.instructions.clicked.connect(self.gotoinstructions)

    def gotoaboutus(self):
        if self.aboutus1 is None:
            self.aboutus1 = welcomepage1()
        else:
            self.aboutus1.show()

    def gotoinstructions(self):
        if self.instructions1 is None:
            self.instructions1 = helpguide1()
            self.instructions1.show()
        else:
            self.instructions1.show()

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
        self.process = None
        uic.loadUi("livetrading.ui", self)
        self.stop.setEnabled(False)
        self.back.clicked.connect(self.gotoback)
        self.start.clicked.connect(self.startB)
        self.stop.clicked.connect(self.stopB)

    def stopB(self):
        t2 = threading.Thread(target=self.KillProcessFunc)
        t2.start()

    def KillProcessFunc(self):
        os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
        self.start.setEnabled(True)

    def startB(self):
        self.start.setEnabled(False)
        self.stop.setEnabled(True)
        t1 = threading.Thread(target=self.ProcessFunc)
        t1.start()

    def ProcessFunc(self):
        root_folder = Path(__file__).parents[2]
        stra = self.comboBox.currentText()
        self.process = subprocess.Popen(
            ['powershell.exe', f'cd {root_folder};.env/Scripts/activate.ps1  ; freqtrade trade --strategy {stra}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        while True:
            output = self.process.stdout.readline()
            self.console.append(output.strip())
            return_code = self.process.poll()
            if return_code is not None:
                print('RETURN CODE', return_code)
                break
            


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
        self.loadInformation()
        self.save.clicked.connect(self.gotosave)
        self.back.clicked.connect(self.gotoback)
        self.cryptopairs.clicked.connect(self.gotocrpytopairs)
        self.stakecombo.activated[str].connect(self.loadStakeCurrency)

    def ComboCurr(self):
        assestList = ["USDT", "BTC", "ETH", "XRP", "LTC", "BCH"]
        for i in assestList:
            self.stakecombo.addItem(i)
        DisplayCurrency = ["USD", "SAR"]
        for j in DisplayCurrency:
            self.stakecombo_2.addItem(j)

    def loadStakeCurrency(self):
        root_folder = Path(__file__).parents[2]
        my_path = root_folder / "config.json"

        with open(my_path, 'r') as jsonFile:
            data = json.load(jsonFile)
            data["stake_currency"] = self.stakecombo.currentText()
        with open(my_path, "w") as jsonFile:
            json.dump(data, jsonFile, indent=2)

    def loadInformation(self):
        root_folder = Path(__file__).parents[2]
        my_path = root_folder / "config.json"

        with open(my_path, 'r') as jsonFile:
            data = json.load(jsonFile)
            self.stakecombo.setCurrentText(str(data["stake_currency"]))
            self.lineEdit.setText(str(data["max_open_trades"]))
            self.stakecombo_2.setCurrentText(str(data["fiat_display_currency"]))
            self.lineEdit_4.setText(str(data["dry_run_wallet"]))
            self.checkBox.setChecked(data["dry_run"])
            if data["stake_amount"] == "unlimited":
                self.lineEdit_2.setText(str(-1))
            else:
                self.lineEdit_2.setText(str(data["stake_amount"]))

    def gotosave(self):
        try:
            # 2022-11-03 11:45:36,147 - freqtrade - ERROR - Starting balance (990 USDT) is smaller than stake_amount 1000 USDT. Wallet is calculated as `dry_run_wallet * tradable_balance_ratio`.

            self.errorL.setText("")
            self.Max_Open_Trades = int(self.lineEdit.text())
            self.Stake_Amount = float(self.lineEdit_2.text())
            self.Wallet_Amount = float(self.lineEdit_4.text())
            self.DisplayCurrency = self.stakecombo_2.currentText()
            self.stakeStr = self.stakecombo.currentText()




            if self.Max_Open_Trades == -1 and self.Stake_Amount == -1:
                raise MOTSTAError
            # stake amount Check
            if (self.Wallet_Amount * 0.99) < self.Stake_Amount:
                raise WASAError
            # check Max open trades
            if self.Max_Open_Trades <= 0:
                if self.Max_Open_Trades == -1:
                    pass
                else:
                    raise MOTError
            # check stake amount
            if self.Stake_Amount <= 0:
                if self.Stake_Amount == -1:
                    self.Stake_Amount = "unlimited"
                else:
                    raise STAError
            # check wallet amount
            if self.Wallet_Amount <= 999:
                raise WAError

            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "config.json"

            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                data["stake_currency"] = self.stakeStr
                data["max_open_trades"] = self.Max_Open_Trades
                data["stake_amount"] = self.Stake_Amount
                data["fiat_display_currency"] = self.DisplayCurrency
                data["dry_run_wallet"] = self.Wallet_Amount
                data["dry_run"] = self.checkBox.isChecked()
            with open(my_path, "w") as jsonFile:
                json.dump(data, jsonFile, indent=2)

            self.errorL.setText("successfully Saved all the information")

        except ValueError:
            self.errorL.setText("First Complete[Max Open Trades, Stake Amount, Wallet] [Only Number] ")
        except MOTError:
            self.errorL.setText("Max Open Trades Must be -1 unlimited  or positive number (1 , 2 , 3 , 4 ...) ")
        except STAError:
            self.errorL.setText("Stake Amount Must be -1 unlimited  or positive number (1 , 2 , 3 , 4 ...) ")
        except WAError:
            self.errorL.setText("Wallet amount must be 1000 or higher ")
        except MOTSTAError:
            self.errorL.setText("both Stake amount and Max open trades cannot be -1 only one can be unlimited")
        except WASAError:
            self.errorL.setText("(Wallet amount * 0.99) must be higher than Stake amount ")

    def gotoback(self):
        window.show()
        self.close()

    def gotocrpytopairs(self):
        self.crypto = CryptoPairs()
        self.crypto.show()


# ----------------backtest interface -----------------------------------------------------------------------------------


class backtesting(QMainWindow):

    def __init__(self):
        super(backtesting, self).__init__()
        uic.loadUi("backtesting.ui", self)
        self.logghandle = QTextEdit
        self.back.clicked.connect(self.gotoback)
        self.start.clicked.connect(self.gotoStart)
        self.download_data.clicked.connect(self.DownloadThread)

    def gotoStart(self):
        self.download_data.setEnabled(False)
        self.start.setEnabled(False)
        t1 = threading.Thread(target=self.processFun)
        t1.start()

    def processFun(self):
        try:
            root_folder = Path(__file__).parents[2]
            if self.comboBox.currentText() == 'Select Strategy':
                raise SelectError
            elif self.comboBox.currentText() == 'Long-term':
                stra = 'Longterm'
            elif self.comboBox.currentText() == 'Medium-term':
                stra = 'MediumTerm'
            else:
                stra = 'ShortTerm'


            process = subprocess.Popen(['powershell.exe',
                                        f'cd {root_folder};.env/Scripts/activate.ps1  ; freqtrade backtesting --strategy {stra}'],
                                       stdout=subprocess.PIPE,
                                       universal_newlines=True)

            while True:
                output = process.stdout.readline()
                if output != "":
                    self.logghandle.append(output.strip())

                # Do something else
                return_code = process.poll()
                # print(return_code)
                if return_code is not None:
                    print('RETURN CODE', return_code)
                    for output in process.stdout.readlines():
                        self.logghandle.append(output.strip())
                    break

            self.download_data.setEnabled(True)
            self.start.setEnabled(True)
            self.logghandle.verticalScrollBar().setValue(self.logghandle.verticalScrollBar().maximum())
        except SelectError:
            self.start.setEnabled(True)
            self.download_data.setEnabled(True)
            self.errorL.setText("Please Select Strategy ")

    def DownloadThread(self):
        self.start.setEnabled(False)
        self.download_data.setEnabled(False)
        t3 = threading.Thread(target=self.downloadData)
        t3.start()

    def downloadData(self):
        try:
            index = self.comboBox_2.currentText()
            if index == "TimeFrame":
                raise SelectError1

            root_folder = Path(__file__).parents[2]
            process = subprocess.Popen(['powershell.exe',
                                        f'cd {root_folder};.env/Scripts/activate.ps1  ; freqtrade download-data --timeframe {index}'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True,
                                       creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            while True:
                output = process.stdout.readline()
                if output != "":
                    self.logghandle.append(output.strip())
                # Do something else
                return_code = process.poll()
                if return_code is not None:
                    print('RETURN CODE', return_code)
                    # Process has finished, read rest of the output
                    for output in process.stdout.readlines():
                        self.logghandle.append(output.strip())
                    break
            self.download_data.setEnabled(True)
            self.start.setEnabled(True)
        except SelectError1:
            self.start.setEnabled(True)
            self.download_data.setEnabled(True)
            self.errorL.setText('Please Select TimeFrame')

    def gotoback(self):
        window.show()
        self.close()


# ----------------Edit Strategy Customization---------------------------------------------------------------------------


class EditStrategy(QMainWindow):

    def __init__(self):
        super(EditStrategy, self).__init__()
        uic.loadUi("editstrategy.ui", self)



        self.comboload()
        self.loadinformation()
        self.appendroi.clicked.connect(self.appendbutton)
        self.deleteroi.clicked.connect(self.deleteb)
        self.back.clicked.connect(self.gotoback)
        self.save.clicked.connect(self.Fsave)
        self.combostr.activated[str].connect(self.loadinformation)

    def comboload(self):
        root_folder = Path(__file__).parents[2]
        my_path = root_folder / "user_data" / "strategies"


        for i in os.listdir(my_path):
            if i.endswith(".json"):
                self.combostr.addItem(i)

    def loadinformation(self):
        self.listroi.clear()
        root_folder = Path(__file__).parents[2]
        my_path = root_folder / "user_data" / "strategies" / self.combostr.currentText()

        # read conditions -------------------------------------------------------------
        # Long Term ------------------------------------
        if self.combostr.currentText() == 'Longterm.json':
            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                RoiList = data["params"]["roi"]
                buy_rsi = data["params"]["buy"]["buy_rsi"]
                enable_buy_macd = data["params"]["buy"]["enable_buy_macd"]
                enable_buy_rsi = data["params"]["buy"]["enable_buy_rsi"]
                sell_rsi = data["params"]["sell"]["sell_rsi"]
                enable_sell_macd = data["params"]["sell"]["enable_sell_macd"]
                enable_sell_rsi = data["params"]["sell"]["enable_sell_rsi"]
                stoploss = data["params"]["stoploss"]["stoploss"]
                trailing_stop = data["params"]["trailing"]["trailing_stop"]
                trailing_stop_positive = data["params"]["trailing"]["trailing_stop_positive"]
                trailing_stop_positive_offset = data["params"]["trailing"]["trailing_stop_positive_offset"]
                trailing_only_offset_is_reached = data["params"]["trailing"]["trailing_only_offset_is_reached"]
            self.ebuystoch.setEnabled(False)
            self.esellstoch.setEnabled(False)
            self.sloss.setText(str((stoploss * 100)))
            self.brsi.setText(str(buy_rsi))
            self.label_22.hide()
            self.label_23.hide()
            self.label_18.setText('Buy RSI')
            self.label_18.adjustSize()
            self.ebmc.setChecked(enable_buy_macd)
            self.ebrc.setChecked(enable_buy_rsi)
            self.srsi.setText(str(sell_rsi))
            self.label_17.setText('Sell RSI')
            self.label_17.adjustSize()
            self.esmc.setChecked(enable_sell_macd)
            self.esrc.setChecked(enable_sell_rsi)
            self.tsp.setText(str((trailing_stop_positive * 100)))
            self.tspo.setText(str((trailing_stop_positive_offset * 100)))
            self.tsc.setChecked(trailing_stop)
            self.toorc.setChecked(trailing_only_offset_is_reached)



        # Long Term Done -------------------------------
        elif self.combostr.currentText() == 'MediumTerm.json':
            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                RoiList = data["params"]["roi"]
                buy_stoch = data["params"]["buy"]["buy_stoch"]
                enable_buy_macd = data["params"]["buy"]["enable_buy_macd"]
                enable_buy_stoch = data["params"]["buy"]["enable_buy_stoch"]
                enable_buy_rsi = data["params"]["buy"]["enable_buy_rsi"]
                sell_stoch = data["params"]["sell"]["sell_stoch"]
                enable_sell_macd = data["params"]["sell"]["enable_sell_macd"]
                enable_sell_stoch = data["params"]["sell"]["enable_sell_stoch"]
                enable_sell_rsi = data["params"]["sell"]["enable_sell_rsi"]
                stoploss = data["params"]["stoploss"]["stoploss"]
                trailing_stop = data["params"]["trailing"]["trailing_stop"]
                trailing_stop_positive = data["params"]["trailing"]["trailing_stop_positive"]
                trailing_stop_positive_offset = data["params"]["trailing"]["trailing_stop_positive_offset"]
                trailing_only_offset_is_reached = data["params"]["trailing"]["trailing_only_offset_is_reached"]

            self.ebuystoch.setEnabled(True)
            self.esellstoch.setEnabled(True)
            self.sloss.setText(str((stoploss * 100)))
            self.brsi.setText(str((buy_stoch * 100)))
            self.label_18.setText('Buy STOCH')
            self.label_18.adjustSize()
            self.label_22.show()
            self.label_23.show()
            self.ebuystoch.setChecked(enable_buy_stoch)
            self.ebmc.setChecked(enable_buy_macd)
            self.ebrc.setChecked(enable_buy_rsi)
            self.srsi.setText(str((sell_stoch * 100)))
            self.label_17.setText('Sell STOCH')
            self.label_17.adjustSize()
            self.esellstoch.setChecked(enable_sell_stoch)
            self.esmc.setChecked(enable_sell_macd)
            self.esrc.setChecked(enable_sell_rsi)
            self.tsp.setText(str((trailing_stop_positive * 100)))
            self.tspo.setText(str((trailing_stop_positive_offset * 100)))
            self.tsc.setChecked(trailing_stop)
            self.toorc.setChecked(trailing_only_offset_is_reached)
        else:
            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                RoiList = data["params"]["roi"]
                stoploss = data["params"]["stoploss"]["stoploss"]
                trailing_stop = data["params"]["trailing"]["trailing_stop"]
                trailing_stop_positive = data["params"]["trailing"]["trailing_stop_positive"]
                trailing_stop_positive_offset = data["params"]["trailing"]["trailing_stop_positive_offset"]
                trailing_only_offset_is_reached = data["params"]["trailing"]["trailing_only_offset_is_reached"]

            self.ebuystoch.setEnabled(False)
            self.esellstoch.setEnabled(False)
            self.esmc.setEnabled(False)
            self.esrc.setEnabled(False)
            self.ebmc.setEnabled(False)
            self.ebrc.setEnabled(False)
            self.ebuystoch.setChecked(False)
            self.esellstoch.setChecked(False)
            self.esmc.setChecked(False)
            self.esrc.setChecked(False)
            self.ebmc.setChecked(False)
            self.ebrc.setChecked(False)

            self.brsi.setEnabled(False)
            self.brsi.setText("")
            self.srsi.setEnabled(False)
            self.srsi.setText('')

            self.sloss.setText(str((stoploss * 100)))
            self.tsp.setText(str((trailing_stop_positive * 100)))
            self.tspo.setText(str((trailing_stop_positive_offset * 100)))
            self.tsc.setChecked(trailing_stop)
            self.toorc.setChecked(trailing_only_offset_is_reached)
        # End of Read Conditions --------------------------------------------------------

        # Roi list Showing --------------------------------------------------------------
        for i in RoiList:
            result = i + ":" + str(RoiList[i] * 100)
            self.listroi.addItem(result)
        self.hroi.setText(str((RoiList["0"] * 100)))

        currValue = 0
        for i in RoiList:
            if eval(i) > currValue:
                currValue = eval(i)
        self.mroi.setText(str(currValue))

        # -----roi Done-------------------------------------------------------------------

    def appendbutton(self):
        try:
            global Rlist
            Rlist = {}
            if eval(self.droi.text()) == 0 or eval(self.droi.text()) is None and float(
                    eval(self.proi.text())) == 0 or float(eval(self.proi.text())) is None:
                raise NoValueError
            durationValue = eval(self.droi.text())
            percValue = eval(self.proi.text())
            highestroi = eval(self.hroi.text())
            maxduration = eval(self.mroi.text())

            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "user_data" / "strategies" / self.combostr.currentText()

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
                Rlist["0"] = (highestroi / 100)
            # Check duration
            for i in RoiList:
                if eval(i) > maxduration:
                    raise MaxDurationIsNotMax
            if MaxDura == durationValue:
                pass
            else:
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
            my_path = root_folder / "user_data" / "strategies" / self.combostr.currentText()

            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                data["params"]["roi"] = Rlist
            with open(my_path, "w") as jsonFile:
                json.dump(data, jsonFile, indent=2)
            self.errorR.setText("")
            self.loadinformation()


        except ValueError:
            self.errorR.setText("Please insert Value in Duration and (%)")
        except TypeError:
            self.errorR.setText("Please insert Value in Duration and (%)")
        except SyntaxError:
            self.errorR.setText("Please insert Value in Duration and (%)")
        except NameError:
            self.errorR.setText("Please insert Only Values in Duration and (%)")
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
        try:
            isitem = self.listroi.selectedItems()
            if not isitem:
                print('nothing to delete')
                return
            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "user_data" / "strategies" / self.combostr.currentText()

            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                RoiList = data["params"]["roi"]
            currentselect = ""
            currentselect = self.listroi.currentItem().text()
            duration, percentage = currentselect.split(":")
            MaxDuration = 0
            # Get Max Duration::
            for i in RoiList:
                if eval(i) > MaxDuration:
                    MaxDuration = eval(i)
            if eval(duration) == 0 or eval(duration) == MaxDuration:
                raise CannotDeleteMaxDuraOrMaxPerc

            # Delete Roi from The List
            RoiList.pop(duration)

            # sort Dict
            RoiList = sorted(RoiList.items(), key=lambda x: x[1], reverse=True)
            RoiList = dict(RoiList)
            with open(my_path, 'r') as jsonFile:
                data = json.load(jsonFile)
                data["params"]["roi"] = RoiList
            with open(my_path, "w") as jsonFile:
                json.dump(data, jsonFile, indent=2)

            self.loadinformation()
            self.errorR.setText(" ")

        except CannotDeleteMaxDuraOrMaxPerc:
            self.errorR.setText("Max Duration and Highest Percentage Cannot be Deleted or Changed from Here ")

    def Fsave(self):
        try:
            root_folder = Path(__file__).parents[2]
            my_path = root_folder / "user_data" / "strategies" / self.combostr.currentText()

            # Check for Trailing Stop Positive Offset Must be bigger than Trailing positive
            if eval(self.tsp.text()) <= 0 or eval(self.tspo.text()) <= 0:
                raise TrailingMustBeBiggerThanZero
            if eval(self.tsp.text()) > eval(self.tspo.text()):
                raise TspMustBeBiggerThanTspo
            # Done Checking Trailing ::
            if self.combostr.currentText() == 'Longterm.json':
                if eval(self.brsi.text()) <= 0 and eval(self.srsi.text()) <= 0:
                    raise BuyAndSellRsiErrorBiggerThanZero

                with open(my_path, 'r') as jsonFile:
                    data = json.load(jsonFile)
                    data["params"]["buy"]["buy_rsi"] = eval(self.brsi.text())
                    data["params"]["buy"]["enable_buy_macd"] = self.ebmc.isChecked()
                    data["params"]["buy"]["enable_buy_rsi"] = self.ebrc.isChecked()
                    data["params"]["sell"]["sell_rsi"] = eval(self.srsi.text())
                    data["params"]["sell"]["enable_sell_macd"] = self.esmc.isChecked()
                    data["params"]["sell"]["enable_sell_rsi"] = self.esrc.isChecked()
                    data["params"]["stoploss"]["stoploss"] = (eval(self.sloss.text()) / 100)
                    data["params"]["trailing"]["trailing_stop"] = self.tsc.isChecked()
                    data["params"]["trailing"]["trailing_stop_positive"] = (eval(self.tsp.text()) / 100)
                    data["params"]["trailing"]["trailing_stop_positive_offset"] = (eval(self.tspo.text()) / 100)
                    data["params"]["trailing"]["trailing_only_offset_is_reached"] = self.toorc.isChecked()
                with open(my_path, "w") as jsonFile:
                    json.dump(data, jsonFile, indent=2)

            elif self.combostr.currentText() == 'MediumTerm.json':
                if eval(self.brsi.text()) <= 0 and eval(self.srsi.text()) <= 0:
                    raise BuyAndSellRsiErrorBiggerThanZero
                if eval(self.brsi.text()) > 99 and eval(self.srsi.text()) > 99:
                    raise BuyAndSellStochPercentage
                with open(my_path, 'r') as jsonFile:
                    data = json.load(jsonFile)
                    data["params"]["buy"]["buy_stoch"] = (eval(self.brsi.text()) / 100)
                    data["params"]["buy"]["enable_buy_macd"] = self.ebmc.isChecked()
                    data["params"]["buy"]["enable_buy_stoch"] = self.ebuystoch.isChecked()
                    data["params"]["buy"]["enable_buy_rsi"] = self.ebrc.isChecked()
                    data["params"]["sell"]["sell_stoch"] = (eval(self.srsi.text()) / 100)
                    data["params"]["sell"]["enable_sell_macd"] = self.esmc.isChecked()
                    data["params"]["sell"]["enable_sell_stoch"] = self.esellstoch.isChecked()
                    data["params"]["sell"]["enable_sell_rsi"] = self.esrc.isChecked()
                    data["params"]["stoploss"]["stoploss"] = (eval(self.sloss.text()) / 100)
                    data["params"]["trailing"]["trailing_stop"] = self.tsc.isChecked()
                    data["params"]["trailing"]["trailing_stop_positive"] = (eval(self.tsp.text()) / 100)
                    data["params"]["trailing"]["trailing_stop_positive_offset"] = (eval(self.tspo.text()) / 100)
                    data["params"]["trailing"]["trailing_only_offset_is_reached"] = self.toorc.isChecked()
                with open(my_path, "w") as jsonFile:
                    json.dump(data, jsonFile, indent=2)
            else:
                with open(my_path, 'r') as jsonFile:
                    data = json.load(jsonFile)
                    data["params"]["stoploss"]["stoploss"] = (eval(self.sloss.text()) / 100)
                    data["params"]["trailing"]["trailing_stop"] = self.tsc.isChecked()
                    data["params"]["trailing"]["trailing_stop_positive"] = (eval(self.tsp.text()) / 100)
                    data["params"]["trailing"]["trailing_stop_positive_offset"] = (eval(self.tspo.text()) / 100)
                    data["params"]["trailing"]["trailing_only_offset_is_reached"] = self.toorc.isChecked()
                with open(my_path, "w") as jsonFile:
                    json.dump(data, jsonFile, indent=2)
            self.errorR_2.setText("")
            self.close()
        except NameError:
            self.errorR_2.setText("Please insert Only Values ")
        except TrailingMustBeBiggerThanZero:
            self.errorR_2.setText("Trailing Stop Positive and Trailing stop Positive offset must be higher than Zero")
        except TspMustBeBiggerThanTspo:
            self.errorR_2.setText("Trailing Stop Positive Must Be Lower Than Trailing Stop Positive Offset")
        except BuyAndSellRsiErrorBiggerThanZero:
            self.errorR_2.setText("Buy And Sell (RSI/Stoch) Must be Higher than 0 ")
        except BuyAndSellStochPercentage:
            self.errorR_2.setText("buy and sell Stoch percentage Must be lower than 100 (0.01 - 99.99) ")

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
        self.availablepairs.doubleClicked.connect(self.insertItemsToSP)
        self.selectedpairs.doubleClicked.connect(self.deleteItemsToAP)
        self.deleteb.clicked.connect(self.deleteItemsToAP)

    def loadInformation(self):
        root_folder = Path(__file__).parents[2]
        my_path1 = root_folder / 'config.json'

        with open(my_path1, 'r') as jsonFile:
            data = json.load(jsonFile)
            self.stakeString = data["stake_currency"]
            self.currencylist = data["exchange"]["pair_whitelist"]
        # check if pair_whitelist == to The quoteAsset in stake currency
        isEqual = True
        for i in self.currencylist:
            base, quote = i.split('/')
            if self.stakeString != quote:
                isEqual = False

        if isEqual:
            for i in self.currencylist:
                self.selectedpairs.addItem(i)
        # else:  # last Change in the File 10/31/2022
        #     with open(my_path1, 'r') as jsonFile:
        #         data = json.load(jsonFile)
        #         data["exchange"]["pair_whitelist"] = []
        #     with open(my_path1, "w") as jsonFile:
        #         json.dump(data, jsonFile, indent=2)

        exchange_info = ClientAPIConn.get_exchange_info()

        for i in exchange_info['symbols']:

            if i['quoteAsset'] == self.stakeString:

                itemsstr = i['baseAsset'] + "/" + i['quoteAsset']
                self.availablepairs.addItem(itemsstr)


        self.availablepairs.sortItems()

    def insertItemsToSP(self):
        isitem = self.availablepairs.selectedItems()
        if not isitem:
            print("nothing to add")
            return


        row = self.availablepairs.currentRow()
        self.selectedpairs.addItem(self.availablepairs.takeItem(row))
        # self.availablepairs.currentItem()

    def deleteItemsToAP(self):
        isitem = self.selectedpairs.selectedItems()
        if not isitem:
            print('nothing to delete')
            return


        row = self.selectedpairs.currentRow()
        self.availablepairs.addItem(self.selectedpairs.takeItem(row))

    def Fsave(self):
        root_folder = Path(__file__).parents[2]
        my_path = root_folder / "config.json"

        with open(my_path, 'r') as jsonFile:
            data = json.load(jsonFile)
            self.stakeString = data["stake_currency"]
            self.currencylist = data["exchange"]["pair_whitelist"]

        isEqual = True
        for i in self.currencylist:
            base, quote = i.split('/')
            if self.stakeString != quote:
                isEqual = False

        if not isEqual:
            data["exchange"]["pair_whitelist"] = []
            with open(my_path, "w") as jsonFile:
                json.dump(data, jsonFile, indent=2)
        # --------------------------------------------------------------------------------------
        items = []
        for x in range(self.selectedpairs.count()):
            items.append(self.selectedpairs.item(x).text())

        root_folder = Path(__file__).parents[2]
        my_path = root_folder / "config.json"


        with open(my_path, 'r') as jsonFile:
            data = json.load(jsonFile)
            data["exchange"]["pair_whitelist"] = items
        with open(my_path, "w") as jsonFile:
            json.dump(data, jsonFile, indent=2)


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


class welcomepage1(QMainWindow):
    def __init__(self):
        super(welcomepage1, self).__init__()
        uic.loadUi('welcomepage.ui', self)
        self.show()
        self.nextb.clicked.connect(self.goNext)

    def goNext(self):
        window.show()
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
        self.login = loginWindow()
        self.close()


class helpguide1(QMainWindow):
    def __init__(self):
        super(helpguide1, self).__init__()
        uic.loadUi('help.ui', self)
        self.nextb.clicked.connect(self.goNext)

    def goNext(self):
        window.show()
        self.close()


# ----------Exceptions handler---------------------------------------------------------------


class Error(Exception):
    pass


class SelectError(Error):
    pass


class SelectError1(Error):
    pass


class MOTError(Error):
    pass


class WASAError(Error):
    pass


class MOTSTAError(Error):
    pass


class STAError(Error):
    pass


class WAError(Error):
    pass


class CannotDeleteMaxDuraOrMaxPerc(Error):
    pass


class SameDuration(Error):
    pass


class SamePerc(Error):
    pass


class DurationHigherThanMax(Error):
    pass


class MaxDurationIsNotMax(Error):
    pass


class BuyAndSellRsiErrorBiggerThanZero(Error):
    pass


class BuyAndSellStochPercentage(Error):
    pass


class percHigherThanMax(Error):
    pass


class TrailingMustBeBiggerThanZero(Error):
    pass


class TspMustBeBiggerThanTspo(Error):
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
