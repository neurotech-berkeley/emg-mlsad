import time
import random
import serial
import subprocess
from datetime import datetime
import tkinter as tk
import random
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne
import mne_qt_browser
from scipy.stats import skew, kurtosis
import scipy.signal as signal
import scipy.stats as stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle

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
        return windows[1:], labels[1:]
    
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
        
        #print("Printing some stats!\n====================")
        #print("Number of samples:", len(processed_windows))
        #print("Number of channels:", len(processed_windows[0][0]))
        #print("====================\n")

        return processed_windows
    
    def create_feature_vector(self, window):
        # window has shape samples x channels
        features = []
        window = np.array(window)
        for channel in window.T:
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
            features.append(kurtosis)
            features.append(skew)
            features.append(num_peaks)
            features.append(num_zero_crossings)

        features = np.array(features)
        return features

    def create_feature_matrix(self, windows):
        # windows has shape windows x samples x channels
        feature_matrix = []
        for window in windows:
            feature_vector = self.create_feature_vector(window)
            feature_matrix.append(feature_vector)

        feature_matrix = np.array(feature_matrix)
        #print("Feature matrix shape:", feature_matrix.shape)
        return feature_matrix
    
    def get_labels(self):
        return self.labels

    def build_data(self, data_path):
        # Load data
        windows, labels = self.load_data(data_path)
        #print("Number of labeled samples:", len(windows))

        # Preprocess data
        windows = self.preprocess_data(windows)

        # Create feature matrix
        X = self.create_feature_matrix(windows)

        # Get labels
        y = labels

        return X, y
    
model = pickle.load(open("model.pkl", "rb"))
data_builder = DataBuilder(sfreq=1000)

def run_inference(window, model):
    feature_vector = data_builder.create_feature_vector(window)
    feature_vector = np.array([feature_vector])
    #print("Feature vector shape:", feature_vector.shape)
    prediction = model.predict(feature_vector)
    return prediction

if __name__ == "__main__":

    port = select_uart_port()
    print("\nOK, opening: ", port)

    serialPort = serial.Serial(port=port, baudrate=115200, bytesize=8, timeout=0.1, stopbits=serial.STOPBITS_ONE)

    running_window = [] # size should be maintained at `window_size`
    window_size = 500
    while serialPort:
        x = serialPort.readline()
        try:
            millis, hall, ch0, ch1, ch2, ch3, ch4 = x.decode("utf-8").split()
        except:
            continue
        millis = int(millis)
        ch0 = int(ch0)
        ch1 = int(ch1)
        ch2 = int(ch2)
        ch3 = int(ch3)
        ch4 = int(ch4)
        hall = int(hall)
        row = [ch0, ch1, ch2, ch3, ch4]
        #print(ch0, ch1, ch2, ch3, ch4)
        
        running_window.append(row)
        if len(running_window) > window_size:
            running_window.pop(0)

        if len(running_window) == window_size:
            prediction = run_inference(running_window, model)
            if prediction == 'tap' or prediction == 'double-tap':
                print("Prediction:", prediction)
                running_window = []
                time.sleep(0.5)


