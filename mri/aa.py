import pandas as pd
import re
from tqdm import tqdm

# Load the CSV file
df = pd.read_csv('/Users/guno/github/TOF/mri/MRI_Regex_with_BSA.csv', encoding='utf-8-sig')

# Find rows where LV EDV(Value) and RV EDV(Value) are the same
matching_rows = df[df['LV EDV(Value)'] == df['RV EDV(Value)']].copy()

# Define the patterns
patterns_lv = {
    "LV EF": re.compile(r"LV.*?Ejection Fraction\s*:\s*([\d\.]+)\s*%", re.DOTALL),
    "LV EDV": re.compile(r"LV.*?End-Diastolic Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
    "LV ESV": re.compile(r"LV.*?End-Systolic Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
    "LV SV": re.compile(r"LV.*?Stroke Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
    "LV CO": re.compile(r"LV.*?Cardiac Output\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*l/min", re.DOTALL | re.IGNORECASE),
    "LV MM": re.compile(r"LV.*?Average Myocardial Mass\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*g", re.DOTALL | re.IGNORECASE),
}

patterns_rv = {
    "RV EF": re.compile(r"RV.*?Ejection Fraction\s*:\s*([\d\.]+)\s*%", re.DOTALL | re.IGNORECASE),
    "RV EDV": re.compile(r"RV.*?End-Diastolic Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
    "RV ESV": re.compile(r"RV.*?End-Systolic Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
    "RV SV": re.compile(r"RV.*?Stroke Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
    "RV CO": re.compile(r"RV.*?Cardiac Output\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*l/min", re.DOTALL | re.IGNORECASE),
    "RV MM": re.compile(r"RV.*?Average Myocardial Mass\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*g", re.DOTALL | re.IGNORECASE),
}

# Function to extract values using regex
def extract_value(text, pattern):
    match = pattern.search(text)
    if match:
        if len(match.groups()) == 1:
            return match.group(1)
        elif len(match.groups()) == 2:
            return match.group(1), match.group(2)
    return None

# Iterate through matching rows
for index, row in tqdm(matching_rows.iterrows(), total=len(matching_rows)):
    text = row['Text']
    
    # Extract values for each LV column
    for key, pattern in patterns_lv.items():
        value = extract_value(text, pattern)
        if value:
            if isinstance(value, tuple):
                matching_rows.at[index, f'{key}(Value)'] = value[0]
                matching_rows.at[index, f'{key}(Index)'] = value[1]
            else:
                matching_rows.at[index, key] = value

    # Extract values for each RV column
    for key, pattern in patterns_rv.items():
        value = extract_value(text, pattern)
        if value:
            if isinstance(value, tuple):
                matching_rows.at[index, f'{key}(Value)'] = value[0]
                matching_rows.at[index, f'{key}(Index)'] = value[1]
            else:
                matching_rows.at[index, key] = value

# Merge the extracted data back into the original dataframe
df.update(matching_rows)

# Save the result to a new CSV file
df.to_csv('/Users/guno/github/TOF/mri/extracted_mri_data_all_rows.csv', index=False)

print(f"Extracted data for {len(matching_rows)} rows and saved to 'extracted_mri_data_all_rows.csv'")