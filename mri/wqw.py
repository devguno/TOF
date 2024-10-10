import pandas as pd
import re

# Load the CSV file into a DataFrame
df = pd.read_csv('/Users/guno/github/TOF/mri/MRI_Regex_with_BSA.csv', encoding='utf-8-sig')

# Compare the LV EDV(Value) and RV EDV(Value) columns
matching_rows = df[df['LV EDV(Value)'] == df['RV EDV(Value)']]

# Define a function to extract values from the text based on the templates
def extract_values_from_text(text):
    result = {}

    # Regular expression for extracting values from the templates
    pattern = r'LV Function Measurement .*?Ejection Fraction : (?P<LV_EF>\d+\.\d+) %.*?End-Diastolic Volume : (?P<LV_EDV>\d+\.\d+) \((?P<LV_EDV_Index>\d+\.\d+)\) ml.*?End-Systolic Volume : (?P<LV_ESV>\d+\.\d+) \((?P<LV_ESV_Index>\d+\.\d+)\) ml.*?Stroke Volume : (?P<LV_SV>\d+\.\d+) \((?P<LV_SV_Index>\d+\.\d+)\) ml.*?Cardiac Output : (?P<LV_CO>\d+\.\d+) .*?Average Myocardial Mass : (?P<LV_MM>\d+\.\d+) \((?P<LV_MM_Index>\d+\.\d+)\) g.*?RV Function Measurement .*?Ejection Fraction : (?P<RV_EF>\d+\.\d+) %.*?End-Diastolic Volume : (?P<RV_EDV>\d+\.\d+) \((?P<RV_EDV_Index>\d+\.\d+)\) ml.*?End-Systolic Volume : (?P<RV_ESV>\d+\.\d+) \((?P<RV_ESV_Index>\d+\.\d+)\) ml.*?Stroke Volume : (?P<RV_SV>\d+\.\d+) \((?P<RV_SV_Index>\d+\.\d+)\) ml.*?Cardiac Output : (?P<RV_CO>\d+\.\d+).*?Average Myocardial Mass : (?P<RV_MM>\d+\.\d+) \((?P<RV_MM_Index>\d+\.\d+)\) g'
    
    match = re.search(pattern, text, re.DOTALL)
    if match:
        result = match.groupdict()
    return result

# Apply the function to the matching rows
matching_rows['Extracted_Values'] = matching_rows['Text'].apply(extract_values_from_text)

# Output the extracted values from the matching rows
extracted_df = matching_rows[['Text', 'Extracted_Values']]

# Save the extracted DataFrame to a new CSV file
output_file_path = '/Users/guno/github/TOF/mri/Extracted_MRI_Data.csv'
extracted_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

# Print a message to confirm saving
print(f"Extracted data has been saved to {output_file_path}")

# Print the first few results for validation
print(extracted_df.head())