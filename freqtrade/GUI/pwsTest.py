import subprocess
from pathlib import Path


root_folder = Path(__file__).parents[2]
print(root_folder)
list = []
process = subprocess.Popen(['powershell.exe',
                            f'cd {root_folder};.env/Scripts/activate.ps1  ; freqtrade backtesting --strategy Longterm'],
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           universal_newlines=True)


while True:
    output = process.stdout.readline()
    if output != "":
        print(output.strip())
    list.append(output.strip())
    if process.poll() is not None:
        print('RETURN CODE', process.poll())
        # Process has finished, read rest of the output
        for output in process.stdout.readlines():
            list.append(output.strip())
            print(output.strip())
        break



print(list)
