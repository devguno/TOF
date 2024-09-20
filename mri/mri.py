import re
import pandas as pd
from tqdm import tqdm

# Load your CSV file
df = pd.read_csv(r'C:\github\TOF\mri\tof_mri.csv')

# Define the regex patterns
patterns = {
    "Delayed Enhancement": re.compile(r"Delayed enhancement", re.DOTALL | re.IGNORECASE),
    "No Delayed Enhancement": re.compile(r"No.*?Delayed enhancement", re.IGNORECASE),
}

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

# Define the columns for the final DataFrame
columns = ['pt_no', 'Date', 'Code', 'Text', 'Delayed Enhancement',
           'LV EF', 'LV EDV(Value)', 'LV EDV(Index)', 'LV ESV(Value)', 'LV ESV(Index)',
           'LV SV(Value)', 'LV SV(Index)', 'LV CO(Value)', 'LV CO(Index)', 'LV MM(Value)', 'LV MM(Index)',
           'RV EF', 'RV EDV(Value)', 'RV EDV(Index)', 'RV ESV(Value)', 'RV ESV(Index)',
           'RV SV(Value)', 'RV SV(Index)', 'RV CO(Value)', 'RV CO(Index)', 'RV MM(Value)', 'RV MM(Index)']

# List to store all results
all_results = []

# Iterate through each row and apply the patterns
for i, row in tqdm(df.iterrows(), total=len(df)):
    text = str(row['value_source_value'])  # Ensure 'text' is treated as a string
    results = {'pt_no': row['pt_no'], 'Date': row['measurement_datetime'], 'Code': row['procedure_source_code'], 'Text': text}

    # Apply general patterns
    for key, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            if key == "No Delayed Enhancement":
                results['Delayed Enhancement'] = "No"
            elif key == "Delayed Enhancement" and 'Delayed Enhancement' not in results:
                results['Delayed Enhancement'] = "Yes"

    # Apply LV patterns
    for key, pattern in patterns_lv.items():
        matches = pattern.findall(text)
        if matches:
            if 'EF' in key:
                results[key] = matches[0]
            else:
                results[key + '(Value)'] = matches[0][0]
                results[key + '(Index)'] = matches[0][1]

    # Apply RV patterns
    for key, pattern in patterns_rv.items():
        matches = pattern.findall(text)
        if matches:
            if 'EF' in key:
                results[key] = matches[0]
            else:
                results[key + '(Value)'] = matches[0][0]
                results[key + '(Index)'] = matches[0][1]

    all_results.append(results)

# Convert results into a DataFrame and keep only the required columns
all_results_df = pd.DataFrame(all_results)
all_results_df = all_results_df[columns]
all_results_df = all_results_df.sort_values(by='Date', ascending=True)
# Save the resulting DataFrame
all_results_df.to_csv('extracted_mri_data.csv', index=False, encoding='utf-8-sig')
