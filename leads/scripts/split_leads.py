import pandas as pd
import numpy as np
import os

# Paths
INPUT_XLSX = 'h:/Source/repos/mvp-research-sheerssoft/leads/WADesk_SenderTemplate.xlsx'
OUTPUT_DIR = 'h:/Source/repos/mvp-research-sheerssoft/leads/splits/'

# 1. Create output directory if not exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. Read the entire Excel file
print(f"Reading {INPUT_XLSX}...")
df = pd.read_excel(INPUT_XLSX)
total_leads = len(df)
print(f"Total leads found: {total_leads}")

# 3. Split into 30 chunks
# Note: np.array_split handles cases where total_leads is not perfectly divisible by 30
chunks = np.array_split(df, 30)

# 4. Save each chunk
for i, chunk in enumerate(chunks, 1):
    file_name = f"T{i}.xlsx"
    output_path = os.path.join(OUTPUT_DIR, file_name)
    chunk.to_excel(output_path, index=False)
    print(f"  [{i}/30] Saved {len(chunk)} leads to {file_name}")

print("\nSplit complete.")
