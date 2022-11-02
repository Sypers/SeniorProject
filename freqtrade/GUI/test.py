import json
from pathlib import Path
import os
import glob
import subprocess

# cmd /k it will remain running the cmd
# cmd /c it will exit from the cmd after execute the command

# stream = os.system('echo hello world')
# print(stream.real)  # check error occurs will be 1 pass will be 0
# os.system('powershell.exe "echo hello world"')
# os.system("ping google.com")

# powershell running in place of get-process here is the command you want
# more than one code put & between them command without output
# subprocess.call('powershell.exe ping google.com', shell=True)

# result= subprocess.getoutput('powershell.exe ls')
# # powershell running with the output
# print(result)


# problem with ip specified
process = subprocess.Popen(['powershell.exe', 'ls'],
                           stdout=subprocess.PIPE,
                           universal_newlines=True)
while True:
    output = process.stdout.readline()
    print(output.strip())
    # Do something else
    return_code = process.poll()
    if return_code is not None:
        print('RETURN CODE', return_code)
        # Process has finished, read rest of the output
        for output in process.stdout.readlines():
            print(output.strip())
        break
process = subprocess.Popen(['powershell.exe', ' ping google.com'],
                           stdout=subprocess.PIPE,
                           universal_newlines=True)

while True:
    output = process.stdout.readline()
    print(output.strip())
    # Do something else
    return_code = process.poll()
    if return_code is not None:
        print('RETURN CODE', return_code)
        # Process has finished, read rest of the output
        for output in process.stdout.readlines():
            print(output.strip())
        break
# --------------------------------------------------------------------




# stream = os.popen('powershell')
# stream = os.pop
# output = stream.read()
# print(output)

# def run(self, cmd =''):
#       completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
#       return completed
#
#
# if __name__ == '__main__':
#       hello_command = "Write-Host 'cd freqtrade/freqtrade/freqtrade/gui'"
#       hello_command = "Write-Host 'poafdsafea'"
#       hello_info = run(hello_command)
#       if hello_info.returncode != 0:
#             print("An error occured: %s", hello_info.stderr)
#       else:
#             print("Hello command executed successfully!")
#
#
#       print("-------------------------")
#
#       bad_syntax_command = "Write-Hst 'Incorrect syntax command!'"
#       bad_syntax_info = run(bad_syntax_command)
#       if bad_syntax_info.returncode != 0:
#             print("An error occured: %s", bad_syntax_info.stderr)
#       else:
#             print("Bad syntax command executed successfully!")

# root_folder = Path(__file__).parents[2]
# my_path = root_folder / "config.json"
# print(my_path)
# with open(my_path, 'r') as jsonFile:
#     print("test1")
#     data = json.load(jsonFile)
#     print("test2")
#     data["max_open_trades"] = 100
#     print("test3")
#     data["stake_amount"] = 300
#     print("test4")
#     data["fiat_display_currency"] = 'USD'
#     print("test5")
#     data["exchange"]["key"] = "notyet"
#     print("test6")
#     data["exchange"]["secret"] = 'self.platformSecret'
#     print("test7")
#     data["dry_run_wallet"] = 1000
#     print("test8")
# with open(my_path, "w") as jsonFile:
#     json.dump(data, jsonFile, indent=2)
# Customization  Strategy
# car = {
#     "brand": "Ford",
#     "model": "Mustang",
#     "year": 1964
# }
# print(car)  # before the change
#
# for i in car:
#     result = i+":"+str(car[i])
#     print(result)
#
#
#
# print(car)  # after the change

# roi= {
#       "0": 0.847,
#       "9487": 0.34199999999999997,
#       "23273": 0.148,
#       "28365": 0,
#       "26000": 0.12
#
# }
# print(roi.pop("26000"))
# print(roi)
# print(float("hihih"))
# print(roi)
# roi = sorted(roi.items(), key=lambda x:x[1] , reverse=True)
# roi = dict(roi)
# print(roi)
# Output: {'Cruyff': 104, 'Eusebio': 120, 'Messi': 125, 'Ronaldo': 132, 'Pele': 150}print(sorted(roi))
# currPerc = 0
# for i in roi:
#     if roi[i] > currPerc:
#         currPerc= roi[i]
# print(currPerc)
# "26000":0.30
# Roi and Duration Exception handle
# x= "26000"
# y= 0.143
# currValue = 0
# for i in roi:
#
#     if eval(i) < eval(x):
#
#         if roi[i] > y:
#             print("pass")
#         else:
#             print("fail")
#     else: pass


# root_folder = Path(__file__).parents[2]
# my_path = root_folder / "user_data" / "strategies"
#
# print(os.listdir(my_path))
# for i in os.listdir(my_path):
#     if i.endswith(".json"):
#         name, ext = i.split('.')
#         print(name)
# print(eval('0'))
