This github repo is mainly inherited from Inga. Only 3 scripts are really important for us.

1. `/dsp/npz_label_recorder.py`: this is the script we used to collect neurowrist data. Running this script will display the action labels so that the subject can perform the corresponding actions. The data will be saved in a .npz file in the folder `/data/unsorted`. Once the data is collected, you should rename it and place it into the folder `/data_named`, so that it could be detected by `mlsad_classification_test.ipynb`.

2. `mlsad_classification_test.ipynb`: this notebook contains the code for feature extraction and several attempts of models for classification. 
    - Running the first block requires to input a number to select a data file from the folder data_named. For now, data_named has 3 previous data files to choose. 
    - The class `DataBuilder` (especially the `create_feature_vector()` method) is where we define feature extraction. It extracts several statistical features (e.g., mean, std, num of peaks, etc.) from each channel of the signals. You chould add or remove features that you want.
    - Once the feature extraction is done, the classification models are really just calling `sklearn`.

3. `live_classification.py`: this script is used to perform real-time classification, written by Abraham and me last week. The idea is just to perform feature extraction and classification for every given length of signal. It is unfinished. You need train a model first and add this trained model to line 337.

P.S. The `\adruino_scipt` folder contains the arduino script for plotting out the signals using Arduino. It is not necessary for the python files above. But if you want to play with Arduino, Manish knows how to use the Arduino.