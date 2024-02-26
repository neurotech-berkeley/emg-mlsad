import numpy as np
import os

# show all list of file names
npz_files = os.listdir("../data/unsorted/")

# Dictionary to hold the combined arrays
combined_arrays = {}
combined_arr_idx = 0
for file in npz_files:
    with np.load(f"../data/unsorted/{file}", allow_pickle=True) as data:
        # Iterate over each array in the npz file
        for arr_name in data.files:
            # You may want to check if arr_name already exists in combined_arrays
            # and handle it accordingly (e.g., rename, merge, etc.)
            combined_arrays[str(combined_arr_idx)] = data[arr_name]
            combined_arr_idx += 1

# Save the combined arrays into a new npz file
np.savez('../data/unsorted/combined_file.npz', **combined_arrays)