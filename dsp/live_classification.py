import serial
import subprocess
from datetime import datetime
import tkinter as tk
import random
import numpy as np
import scipy.signal as signal
import scipy.stats as stats


# class DataRecorder:
#     def __init__(self):
#         # self.fieldnames = ['millis', 'hall', 'ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'event']
#         self.fieldnames = ['millis', 'hall', 'ch0', 'ch2', 'ch3', 'ch4', 'event']
#         self.event_label = None
#         self.event_labels = ["rest", "thumb-to-index", "thumb-to-pinky", "clench"]
#         self.root = tk.Tk()
#         self.root.title("Data Recorder")
#         self.root.geometry("500x300")
#         self.root.eval('tk::PlaceWindow . center')
#         self.label = tk.Label(self.root, text="Initializing...", font=("Helvetica", 36))
#         self.label.pack(pady=20, anchor="center")
#         self.root.after(0, self.start_recording)
#         self.window_closed = False

#         self.data_dict = {}
#         self.current_window = []
#         self.data_ready = False

#     def start_recording(self):
#         self.label.configure(text="Rest", font=("Helvetica", 36))
#         self.label.pack(pady=20, anchor="center")
#         self.event_label = "rest"
#         self.root.after(25000, self.flash_text)
#         self.root.after(300000, self.stop_recording)

#     def flash_text(self):
#         label = self.event_label
#         data = self.current_window
#         sample_dict = {"label": label, "data": data}
#         self.data_dict[len(self.data_dict)] = sample_dict
#         self.current_window = []
#         event_index = self.event_labels.index(self.event_label)

#         if event_index < len(self.event_labels) - 1:
#             self.label.configure(text=self.event_labels[event_index + 1], font=("Helvetica", 36))
#             self.event_label = self.event_labels[event_index + 1]

#         else:
#             self.label.configure(text=self.event_labels[0], font=("Helvetica", 36))
#             self.event_label = self.event_labels[0]

#         # if self.event_label == "thumb-to-index":
#         #     self.label.configure(text="Thumb to Middle", font=("Helvetica", 36))
#         #     self.event_label = "thumb-to-middle"

#         # elif self.event_label == "thumb-to-middle":
#         #     self.label.configure(text="Thumb to Ring", font=("Helvetica", 36))
#         #     self.event_label = "thumb-to-ring"

#         # elif self.event_label == "thumb-to-ring":
#         #     self.label.configure(text="Thumb to Pinky", font=("Helvetica", 36))
#         #     self.event_label = "thumb-to-pinky"
        
#         # elif self.event_1
#         # label == "thumb-to-pinky":
#         #     self.label.configure(text="Double Tap", font=("Helvetica", 36))
#         #     self.event_label = "double-tap"

#         # elif self.event_label == "double-tap":
#         #     self.label.configure(text="Tap", font=("Helvetica", 36))
#         #     self.event_label = "tap"
        
#         # elif self.event_label == "tap":
#         #     self.label.configure(text="Rest", font=("Helvetica", 36))
#         #     self.event_label = "rest"
       
#         # else:
#         #     self.label.configure(text="Thumb to Index", font=("Helvetica", 36))
#         #     self.event_label = "thumb-to-index"

#         self.root.after(random.randint(1500, 3000), self.flash_text)

#     def stop_recording(self):
#         self.data_ready = True
#         self.label.configure(text="Saving and closing...", font=("Helvetica", 16))
#         self.label.pack(pady=20, anchor="center")
#         self.root.after(2000, self.save_and_destroy)
#         self.window_closed = True

#     def save_and_destroy(self):
#         self.root.destroy()

#     def run(self):
#         self.root.mainloop()

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


class DataBuilder:
    def __init__(self, sfreq):
        self.sfreq = sfreq

    def load_data(self, data_path):
        # Load the .npz file
        data = np.load(data_path, allow_pickle=True)
        labels = []
        windows = []
        for key in data.files:
            label = data[key].item()['label']
            window = data[key].item()['data']
            labels.append(label)
            windows.append(window)
        # dropping the first window because it's "rest"
        # drop the last window too
        return windows[1:-1], labels[1:-1]
    
    def load_window(self, data_path, index):
        # Load the .npz file
        windows, labels = self.load_data(data_path)
        windows = self.preprocess_data(windows)
        return windows[index], labels[index]

    def preprocess_data(self, windows):
        # remove the first two columns of each window (millis and hall sensor)
        processed_windows = []
        for window in windows:
            window = np.delete(window, [0,1], axis=1)
            processed_windows.append(window)
        
        print("Printing some stats!\n====================")
        print("Number of samples:", len(processed_windows))
        print("Number of channels:", len(processed_windows[0][0]))
        print("====================\n")

        return processed_windows
    
    def create_feature_vector(self, window):
        # window has shape samples x channels
        features = []
        print("Window shape:", window.shape)
        for channel in window.T:
            # extract mean and std
            mean = np.mean(channel)
            std = np.std(channel)

            # demean and normalize
            channel = channel - np.mean(channel)
            channel = channel / np.std(channel)

            # calculate features
            kurtosis = stats.kurtosis(channel)
            skew = stats.skew(channel)
            # find peaks
            peaks, _ = signal.find_peaks(channel)
            num_peaks = len(peaks)
            # find zero crossings
            zero_crossings = np.where(np.diff(np.sign(channel)))[0]
            num_zero_crossings = len(zero_crossings)

            # IEMG
            iemg = np.sum(np.abs(channel))
            # print("IEMG:", iemg)

            # MAV
            mav = np.mean(np.abs(channel))
            # print("MAV:", mav)

            # SSI
            ssi = np.sum(np.square(channel))
            # print("SSI:", ssi)

            # RMS
            rms = np.sqrt(np.mean(np.square(channel)))
            # print("RMS:", rms)

            # VAR
            var = np.var(channel)
            # print("VAR:", var)

            # Myopulse Percentage Rate
            t_mmp = 0.1
            mmp = np.sum(np.abs(channel) > t_mmp) / len(channel)
            # print("MMP:", mmp)

            # Waveform Length
            wl = np.sum(np.abs(np.diff(channel)))
            # print("WL:", wl)

            # DAMV
            damv = np.mean(np.abs(np.diff(channel)))
            # print("DAMV:", damv)

            # M2
            m2 = np.sum(np.square(np.diff(channel)))
            # print("M2:", m2)

            # DVARV
            dvarv = np.mean(np.square(np.diff(channel)))
            # print("DVARV:", dvarv)

            # DASDV
            dasdv = np.sqrt(np.mean(dvarv))
            # print("DASDV:", dasdv)

            # WAMP
            t_wamp = 0.1
            wamp = np.sum(np.abs(np.diff(channel)) > t_wamp)
            # print("WAMP:", wamp)

            # inegerated absolute of second derivative
            iasd = np.sum(np.abs(np.diff(np.diff(channel))))

            # integrated absolute third derivative
            iatd = np.sum(np.abs(np.diff(np.diff(np.diff(channel)))))

            # integerated exponential of absolute value
            # ieav = np.sum(np.exp(np.abs(channel)))
            # print("IEAV:", ieav)

            # integerated absolute log value
            # ialv = np.sum(np.log(np.abs(channel) + 0.1))
            # print("IALV:", ialv)
            # print(np.min(channel))
            # print(np.max(channel))
            # print(np.isnan(channel).any())

            # integrated exponential
            ie = np.sum(np.exp(channel))

            features.append(kurtosis)
            features.append(skew)
            features.append(num_peaks)
            features.append(num_zero_crossings)
            # features.append(mean)
            # features.append(std)
            #features.append(iemg)
            # features.append(mav)
            #features.append(ssi)
            # features.append(rms)
            features.append(var)
            #features.append(mmp)
            #features.append(wl)
            # features.append(damv)
            #features.append(m2)
            #features.append(dvarv)
            #features.append(dasdv)
            #features.append(wamp)
            #features.append(iasd)
            #features.append(iatd)
            # features.append(ieav)
            # features.append(ialv)
            #features.append(ie)

        features = np.array(features)
        return features

    def create_feature_matrix(self, windows):
        # windows has shape windows x samples x channels
        feature_matrix = []
        for window in windows:
            feature_vector = self.create_feature_vector(window)
            feature_matrix.append(feature_vector)

        feature_matrix = np.array(feature_matrix)
        print("Feature matrix shape:", feature_matrix.shape)
        return feature_matrix
    
    def get_labels(self):
        return self.labels

    def build_data(self, data_path):
        # Load data
        windows, labels = self.load_data(data_path)
        print("Number of labeled samples:", len(windows))

        # Preprocess data
        windows = self.preprocess_data(windows)

        # Create feature matrix
        X = self.create_feature_matrix(windows)

        # Get labels
        y = labels

        return X, y

if __name__ == "__main__":

    port = select_uart_port()
    print("\nOK, opening: ", port)

    serialPort = serial.Serial(port=port, baudrate=115200, bytesize=8, timeout=0.1, stopbits=serial.STOPBITS_ONE)
    # data_recorder = DataRecorder()
    data_builder = DataBuilder(sfreq=1000)

    current_window = []
    window_length = 1000
    step_length = 10

    while serialPort:
        # read in the data at current time point
        x = serialPort.readline()
        try:
            millis, hall, ch0, ch1, ch2, ch3, ch4 = x.decode("utf-8").split()[1:]
            # millis, hall, ch0, ch2, ch3, ch4 = x.decode("utf-8").split()[1:]
        except:
            continue
        millis = int(millis)
        ch0 = int(ch0)
        ch1 = int(ch1)
        ch2 = int(ch2)
        ch3 = int(ch3)
        ch4 = int(ch4)
        hall = int(hall)
        # row = [millis, hall, ch0, ch1, ch2, ch3, ch4, data_recorder.event_label]
        row = [ch0, ch1, ch2, ch3, ch4]
        print(row)
        # append the data at current time point into the current time window
        current_window.append(row)

        # do classification every window_length samples
        if len(current_window) == window_length:
            
            # feature extraction
            features = data_builder.create_feature_vector(np.array(current_window))

            # use some trained model to predict the action
            """print(model.predict(features)) #do something here"""

            # pop out the first elements in the current window, ready for the next window
            current_window = current_window[step_length::]


        # if data_recorder.data_ready:
        #     now = datetime.now()
        #     dt_string = now.strftime("%m-%d-%Y-%H:%M:%S")
            
        #     # Convert keys to strings before saving
        #     data_dict_str_keys = {str(key): value for key, value in data_recorder.data_dict.items()}
            
        #     break

        # if data_recorder.window_closed:
        #     break
