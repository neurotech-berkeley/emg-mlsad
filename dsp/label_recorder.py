import csv
import serial
import subprocess
from datetime import datetime
import tkinter as tk
from threading import Thread
import random

class DataRecorder:
    def __init__(self, save_as_csv):
        self.save_as_csv = save_as_csv
        self.fieldnames = ['millis', 'hall', 'ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'event']
        self.writer = None
        self.event_label = None
        self.root = tk.Tk()
        self.root.title("Data Recorder")
        self.root.geometry("500x300")
        self.root.eval('tk::PlaceWindow . center')
        self.label = tk.Label(self.root, text="Initializing...", font=("Helvetica", 36))
        self.label.pack(pady=20, anchor="center")
        self.root.after(0, self.start_recording)
        self.window_closed = False

        self.current_data = []

    def start_recording(self):
        self.csvfile = open(self.save_as_csv, "w", newline="")
        self.writer = csv.DictWriter(self.csvfile, fieldnames=self.fieldnames)
        self.writer.writeheader()

        self.label.configure(text="Rest", font=("Helvetica", 36))
        self.label.pack(pady=20, anchor="center")
        self.event_label = "rest"
        self.root.after(10000, self.flash_text)
        self.root.after(20000, self.stop_recording)

    def flash_text(self):
        if self.writer and not self.csvfile.closed:
            if self.event_label == "tap":
                self.label.configure(text="Double-Tap", font=("Helvetica", 36))
                self.label.pack(pady=20, anchor="center")
                self.event_label = "double-tap"
            else:
                self.label.configure(text="Tap", font=("Helvetica", 36))
                self.label.pack(pady=20, anchor="center")
                self.event_label = "tap"

            self.root.after(random.randint(1500, 3000), self.flash_text)

    def stop_recording(self):
        if self.writer and not self.csvfile.closed:
            self.label.configure(text="Saving and closing...", font=("Helvetica", 16))
            self.label.pack(pady=20, anchor="center")
            self.csvfile.close()
            self.window_closed = True
            self.root.after(2000, self.root.destroy)

    def run(self):
        self.root.mainloop()

def select_uart_port():
    output = subprocess.run(["ls /dev/tty.*"], stdout=subprocess.PIPE, shell=True, text=True)
    ports = output.stdout.split("\n")[:-1]
    i = 0
    print("\n>> Select UART/USB to read from:\n")
    for port in ports:
        print("  ", i, ":", port)
        i += 1
    index = int(input("\n>> "))
    return ports[index]

if __name__ == "__main__":
    now = datetime.now()
    dt_string = now.strftime("%m-%d-%Y-%H:%M:%S")
    save_as_csv = f"../data/unsorted/{dt_string}.csv"
    print(save_as_csv)

    port = select_uart_port()
    print("\nOK, opening: ", port)

    serialPort = serial.Serial(port=port, baudrate=115200, bytesize=8, timeout=0.1, stopbits=serial.STOPBITS_ONE)

    data_recorder = DataRecorder(save_as_csv)
    # data_recorder_thread = Thread(target=data_recorder.run)
    # data_recorder_thread.start()

    while serialPort:
        x = serialPort.readline()
        try:
            millis, hall, ch0, ch1, ch2, ch3, ch4 = x.decode("utf-8").split()[1:]
        except:
            continue
        millis = int(millis)
        ch0 = int(ch0)
        ch1 = int(ch1)
        ch2 = int(ch2)
        ch3 = int(ch3)
        ch4 = int(ch4)
        hall = int(hall)
        print(millis, hall, ch0, ch1, ch2, ch3, ch4, data_recorder.event_label)
        if data_recorder.writer and not data_recorder.csvfile.closed:
            data_recorder.writer.writerow({
                'millis': millis,
                'hall': hall,
                'ch0': ch0,
                'ch1': ch1,
                'ch2': ch2,
                'ch3': ch3,
                'ch4': ch4,
                'event': data_recorder.event_label
            })

        if not data_recorder.window_closed:
            data_recorder.root.update_idletasks()
            data_recorder.root.update()
        else:
            break

    # data_recorder_thread.join()
