import pandas as pd
import os

# Read the original CSV file
input_csv = 'product_links.csv'  # Replace with your original CSV file path
df = pd.read_csv(input_csv)


# Determine the number of rows per split
total_rows = df.shape[0]
rows_per_split = total_rows // 100
extra_rows = total_rows % 100

# Create folders if they don't exist
folders = ['a', 'b', 'c', 'd']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Split the DataFrame into 100 smaller DataFrames and save to CSV files
start_idx = 0

for i in range(100):
    if extra_rows > 0:
        end_idx = start_idx + rows_per_split + 1
        extra_rows -= 1
    else:
        end_idx = start_idx + rows_per_split

    split_df = df[start_idx:end_idx]
    folder_name = folders[i // 25]
    split_df.to_csv(f'./{folder_name}/split_{i+1}.csv', index=False)

    start_idx = end_idx

print("CSV files have been split and saved into folders a, b, c, and d.")