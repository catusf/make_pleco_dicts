import json

import json
import pandas as pd

# Load JSON dictionary
with open('wordlists/radical_set.json', 'r', encoding='utf-8') as f:
    json_dict = json.load(f)

# Read the Excel file
excel_data = pd.read_excel('wordlists/radicals-vietnamese.xlsx')

# Assume the Excel file has columns: 'key', 'attribute1', 'attribute2', ...
for _, row in excel_data.iterrows():
    key = row['radical']  # Assuming the column 'key' exists
    if key in json_dict:
        # Add new attributes to the key
        for column in row.index:
            if column != 'radical':  # Exclude the key column itself
                json_dict[key][column] = row[column].strip()

# Save the updated JSON dictionary back to file
with open('wordlists/radical_set-updated.json', 'w', encoding='utf-8') as f:
    json.dump(json_dict, f, ensure_ascii=False, indent=4)

print("Attributes added successfully!")
