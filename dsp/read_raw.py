"""

This code reads unlabeled data from Neurowrist and saves it to a CSV file:
../../data/unsorted/{}.csv

"""

import csv
import serial # pip3 install pyserial
import subprocess
from datetime import datetime

now = datetime.now()
dt_string = now.strftime("%m-%d-%Y-%H:%M:%S")
save_as_csv =  "../data/unsorted/{}.csv".format(dt_string)
print(save_as_csv)

output = subprocess.run(["ls /dev/tty.*"], stdout=subprocess.PIPE, shell=True, text=True)
ports = output.stdout.split("\n")[:-1]
i = 0
print("\n>> Select UART/USB to read from:\n")
for port in ports:
    print("  ", i, ":", port)
    i += 1
index = int(input("\n>> "))
port = ports[index]
print("\nOK, opening", port)

serialPort = serial.Serial(port=port, baudrate=115200,
                           bytesize=8, timeout=0.1, stopbits=serial.STOPBITS_ONE)

# create a CSV file to store the data
csvfile = open(save_as_csv, "w", newline="")
fieldnames = ['millis', 'hall', 'ch0', 'ch1', 'ch2', 'ch3', 'ch4']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()
while serialPort:
    x = serialPort.readline()
    try: 
        millis, hall, ch0, ch1, ch2, ch3, ch4 = x.decode("utf-8").split()[1:]
    except KeyboardInterrupt:
        print("saved to:\n", save_as_csv)
        csvfile.close()
    except:
        continue

    millis = int(millis)
    ch0 = int(ch0)
    ch1 = int(ch1)
    ch2 = int(ch2)
    ch3 = int(ch3)
    ch4 = int(ch4)
    hall = int(hall)
    print(millis, hall, ch0, ch1, ch2, ch3, ch4)
    writer.writerow({'millis': millis, 'hall': hall, 'ch0': ch0, 'ch1': ch1, 'ch2': ch2, 'ch3': ch3, 'ch4': ch4})