import re
import pandas as pd
import numpy as np
from datetime import datetime

def define_patterns():
    patterns = {
        "EF": re.compile(r"Ejection Fraction\s*:\s*([\d\.]+)\s*%", re.IGNORECASE),
        "EDV": re.compile(r"End-Diastolic Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.IGNORECASE),
        "ESV": re.compile(r"End-Systolic Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.IGNORECASE),
        "SV": re.compile(r"Stroke Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.IGNORECASE),
        "CO": re.compile(r"Cardiac Output\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*l/min", re.IGNORECASE),
        "mass": re.compile(r"(?:Average Myocardial Mass|mass)\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*g", re.IGNORECASE),
    }
    
    patterns_measurement = {
        "BSA": re.compile(r"BSA\s*:\s*([\d\.]+)\s*m2", re.IGNORECASE),
        "HR": re.compile(r"Heart Rate\s*:\s*([\d\.]+)\s*bpm", re.IGNORECASE),
    }
    
    return patterns, patterns_measurement

def detect_format(text):
    if re.search(r"\d+\.\s*(?:Morphology|Regurgitation|Flow Measurement|Ventricular Function)", text, re.DOTALL | re.IGNORECASE):
        return "compact"
    elif re.search(r"(?:LV|LV2|RV)\s*Function Measurement", text, re.DOTALL | re.IGNORECASE):
        return "sectioned"
    elif re.search(r"LV\s+RV", text, re.DOTALL | re.IGNORECASE):
        return "side_by_side"
    elif re.search(r"(?:LV|RV).*?EF.*?(?:LV|RV).*?EF", text, re.DOTALL | re.IGNORECASE):
        return "table"
    else:
        return "unknown"
    
    
def extract_date(date_string):
    try:
        # Parse the date string
        date = pd.to_datetime(date_string)
        # Format the date as 'YYYY-MM-DD'
        return date.strftime('%Y-%m-%d')
    except:
        return None


def extract_data(text, patterns, patterns_measurement):
    results = {}
    format_type = detect_format(text)
    results['Format'] = format_type
    
    if format_type in ["compact", "sectioned"]:
        # Extract LV and RV data for sectioned and compact format
        for ventricle in ['LV', 'LV2', 'RV']:
            section_pattern = re.compile(rf"{ventricle}\s*Function Measurement.*?(?=(?:LV|LV2|RV)\s*Function Measurement|\Z)", re.DOTALL | re.IGNORECASE)
            section = section_pattern.search(text)
            if section:
                section_text = section.group(0)
                for key, pattern in patterns.items():
                    match = pattern.search(section_text)
                    if match:
                        results[f"{ventricle} {key}"] = match.group(1)
                        if len(match.groups()) > 1 and match.group(2):
                            results[f"{ventricle} {key}(Index)"] = match.group(2)
        
        # If LV2 data exists, use it instead of LV
        if any(key.startswith('LV2') for key in results):
            for key in list(results.keys()):
                if key.startswith('LV '):
                    lv2_key = key.replace('LV ', 'LV2 ')
                    if lv2_key in results:
                        results[key] = results[lv2_key]
                        del results[lv2_key]
        
        if format_type == "compact":
            ventricular_function = re.search(r"Ventricular Function(.*?)(?:\Z)", text, re.DOTALL | re.IGNORECASE)
            if ventricular_function:
                vf_text = ventricular_function.group(1)
                for ventricle in ['LV', 'RV']:
                    for key, pattern in patterns.items():
                        match = re.search(rf"{ventricle}\s+{key}\s*:\s*([\d\.]+)(?:\s*\(([\d\.]+)\))?", vf_text, re.IGNORECASE)
                        if match:
                            results[f'{ventricle} {key}'] = match.group(1)
                            if match.group(2):
                                results[f'{ventricle} {key}(Index)'] = match.group(2)
    
    elif format_type in ["table", "side_by_side"]:
        # Extract data for table and side_by_side format
        if format_type == "table":
            lv_rv_pattern = re.compile(r"(?:LV|RV)\s*EF\s*([\d\.]+)%.*?(?:LV|RV)\s*EF\s*([\d\.]+)%.*?EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?(?:CO|cardiac output)\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?.*?(?:CO|cardiac output)\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?", re.DOTALL | re.IGNORECASE)
        else:  # side_by_side
            lv_rv_pattern = re.compile(r"LV\s+RV.*?EF\s*([\d\.]+)%\s+EF\s*([\d\.]+)%.*?EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?\s+EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?\s+ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?\s+SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?CO\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?\s+CO\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?", re.DOTALL | re.IGNORECASE)
        
        lv_rv_match = lv_rv_pattern.search(text)
        if lv_rv_match:
            groups = lv_rv_match.groups()
            if len(groups) >= 18:
                if format_type == "table" and 'RV' in text.split('EF')[0].split('\n')[-1]:
                    results['RV EF'], results['LV EF'] = groups[0], groups[1]
                    results['RV EDV'], results['RV EDV(Index)'] = groups[2], groups[3]
                    results['LV EDV'], results['LV EDV(Index)'] = groups[4], groups[5]
                    results['RV ESV'], results['RV ESV(Index)'] = groups[6], groups[7]
                    results['LV ESV'], results['LV ESV(Index)'] = groups[8], groups[9]
                    results['RV SV'], results['RV SV(Index)'] = groups[10], groups[11]
                    results['LV SV'], results['LV SV(Index)'] = groups[12], groups[13]
                    results['RV CO'], results['RV CO(Index)'] = groups[14], groups[15]
                    results['LV CO'], results['LV CO(Index)'] = groups[16], groups[17]
                else:
                    results['LV EF'], results['RV EF'] = groups[0], groups[1]
                    results['LV EDV'], results['LV EDV(Index)'] = groups[2], groups[3]
                    results['RV EDV'], results['RV EDV(Index)'] = groups[4], groups[5]
                    results['LV ESV'], results['LV ESV(Index)'] = groups[6], groups[7]
                    results['RV ESV'], results['RV ESV(Index)'] = groups[8], groups[9]
                    results['LV SV'], results['LV SV(Index)'] = groups[10], groups[11]
                    results['RV SV'], results['RV SV(Index)'] = groups[12], groups[13]
                    results['LV CO'], results['LV CO(Index)'] = groups[14], groups[15]
                    results['RV CO'], results['RV CO(Index)'] = groups[16], groups[17]
    
    # Extract other measurements
    for key, pattern in patterns_measurement.items():
        match = pattern.search(text)
        if match:
            results[key] = match.group(1)
    
    # Extract Delayed Enhancement
    delayed_enhancement = re.search(r"Delayed enhancement.*", text, re.IGNORECASE)
    if delayed_enhancement:
        results['Delayed Enhancement'] = delayed_enhancement.group(0)
    else:
        results['Delayed Enhancement'] = ""
    
    # Extract PR and TR information
    pr_match = re.search(r"(No|Trivial|Mild|Moderate to severe|Moderate|Severe)\s+PR", text, re.IGNORECASE)
    if pr_match:
        results["PR"] = pr_match.group(1)
    
    tr_match = re.search(r"(No|Trivial|Mild|Moderate to severe|Moderate|Severe)\s+TR", text, re.IGNORECASE)
    if tr_match:
        results["TR"] = tr_match.group(1)
    
    return results

def extract_date(text):
    date_pattern = re.compile(r"(\d{4}[-.]\d{1,2}[-.]\d{1,2})")
    match = date_pattern.search(text)
    if match:
        date_str = match.group(1).replace('.', '-')
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    return None

def process_row(row, patterns, patterns_measurement):
    text = row['value_source_value']
    format_type = detect_format(text)
    result = extract_data(text, patterns, patterns_measurement)
    result['Date'] = extract_date(row['measurement_datetime'])
    result['pt_no'] = row['pt_no']
    result['Code'] = row['procedure_source_code']
    result['Text'] = text
    result['Format'] = format_type
    return result

def calculate_missing_ratio(row, columns_to_check):
    """Calculate the ratio of missing values in a row."""
    total = len(columns_to_check)
    missing = sum(pd.isna(row[col]) or row[col] == '' for col in columns_to_check)
    return missing / total

def process_csv(input_file):
    patterns, patterns_measurement = define_patterns()
    
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    
    all_results = []
    for index, row in df.iterrows():
        try:
            result = process_row(row, patterns, patterns_measurement)
            all_results.append(result)
        except Exception as e:
            print(f"Error processing row {index} (pt_no: {row['pt_no']}): {str(e)}")
    return all_results

def save_to_csv(all_results, output_file):
    columns = ['pt_no', 'Date', 'Code', 'Format', 'Text', 'Delayed Enhancement', 'BSA', 'PR', 'TR',
               'LV EF', 'LV EDV', 'LV EDV(Index)', 'LV ESV', 'LV ESV(Index)',
               'LV SV', 'LV SV(Index)', 'LV CO', 'LV CO(Index)', 'LV mass', 'LV mass(Index)',
               'RV EF', 'RV EDV', 'RV EDV(Index)', 'RV ESV', 'RV ESV(Index)',
               'RV SV', 'RV SV(Index)', 'RV CO', 'RV CO(Index)', 'RV mass', 'RV mass(Index)']

    df = pd.DataFrame(all_results)
    
    for col in columns:
        if col not in df.columns:
            df[col] = ''

    df = df[columns]

    # Calculate missing ratio, excluding 'Text' column
    columns_to_check = [col for col in columns if col != 'Text']
    df['Missing_Ratio'] = df.apply(lambda row: calculate_missing_ratio(row, columns_to_check), axis=1)
    
    # Add 'High_Missing' column
    df['High_Missing'] = np.where(df['Missing_Ratio'] >= 0.5, 1, 0)

    # Reorder columns to place 'High_Missing' after 'Format'
    new_columns = columns[:4] + ['High_Missing'] + columns[4:]
    df = df[new_columns]

    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Data extracted and saved to {output_file}")

    # Print summary of high missing rows
    high_missing_count = df['High_Missing'].sum()
    total_rows = len(df)
    print(f"Number of rows with high missing data (>=50%): {high_missing_count} out of {total_rows} ({high_missing_count/total_rows:.2%})")

if __name__ == "__main__":
    input_file = r'C:\Users\Roh\Documents\GitHub\TOF\mri\tof_mri.csv'
    output_file = r'C:\Users\Roh\Documents\GitHub\TOF\mri\extracted_mri_data.csv'
    
    all_results = process_csv(input_file)
    save_to_csv(all_results, output_file)
    
    # For demonstration, print the first result
    if all_results:
        print("First extracted result:")
        for key, value in all_results[0].items():
            if key != 'Text':  # Exclude the full text to keep the output concise
                print(f"{key}: {value}")
    else:
        print("No data extracted")