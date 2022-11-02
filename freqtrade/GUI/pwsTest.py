import subprocess
from pathlib import Path


root_folder = Path(__file__).parents[2]
print(root_folder)

process = subprocess.Popen(['powershell.exe', f'cd {root_folder};.env/Scripts/activate.ps1  ; freqtrade trade --strategy ShortTerm'],
                           stdout=subprocess.PIPE,
                           universal_newlines=True)
while True:
    output = process.stdout.readline()
    print(output.strip())
    # Do something else
    return_code = process.poll()
    # print(return_code)
    if return_code is not None:
        print('RETURN CODE', return_code)
        # Process has finished, read rest of the output
        for output in process.stdout.readlines():
           print(output.strip())
        break