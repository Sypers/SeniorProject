import json
from pathlib import Path
import os



root_folder = Path(__file__).parents[2]
my_path = root_folder / "config.json"
print(my_path)
with open(my_path, 'r') as jsonFile:
    print("test1")
    data = json.load(jsonFile)
    print("test2")
    data["max_open_trades"] = 100
    print("test3")
    data["stake_amount"] = 300
    print("test4")
    data["fiat_display_currency"] = 'USD'
    print("test5")
    data["exchange"]["key"] = "notyet"
    print("test6")
    data["exchange"]["secret"] = 'self.platformSecret'
    print("test7")
    data["dry_run_wallet"] = 1000
    print("test8")
with open(my_path, "w") as jsonFile:
    json.dump(data, jsonFile, indent=2)