from datetime import datetime
from os.path import abspath
import os.path
here = abspath(".")
now =  datetime.now().strftime("%d/%m/%Y %H:%M:%S")
print(f'hello from : {here} at { now }')
f = open(f'{os.path.join(here, "now.txt")}', "w")
f.write(f"{here} - {now}")
f.close()
