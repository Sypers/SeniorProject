import json
from pathlib import Path
import os
import glob

#
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

roi= {
      "0": 0.847,
      "9487": 0.34199999999999997,
      "23273": 0.148,
      "28365": 0,
      "26000": 0.12

}
print(roi.pop("26000"))
print(roi)
print(float("hihih"))
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
#"26000":0.30
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
