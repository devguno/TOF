import re
import pandas as pd
from tqdm import tqdm


def define_patterns():
    """Define improved regex patterns for data extraction."""
    patterns = {
        "Delayed Enhancement": re.compile(r"(?:LGE|DE)\s*(?:\+|\(\+\)|-|\(-\)).*?(?:at|in)?.*?(?:RV|LV)?.*?(?:insertion|wall)?", re.IGNORECASE | re.DOTALL),
        "BSA": re.compile(r"(?:BSA|Body surface area)\s*[:=]\s*([\d\.]+)\s*(?:m\^2|M2)", re.IGNORECASE),
    }

    patterns_measurement = {
        "EF": re.compile(r"Ejection Fraction\s*[:=]\s*([\d\.]+)\s*%", re.DOTALL | re.IGNORECASE),
        "EDV": re.compile(r"End-Diastolic Volume\s*[:=]\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
        "ESV": re.compile(r"End-Systolic Volume\s*[:=]\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
        "SV": re.compile(r"Stroke Volume\s*[:=]\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
        "CO": re.compile(r"Cardiac Output\s*[:=]\s*([\d\.]+)\s*\(([\d\.]+)\)\s*l/min", re.DOTALL | re.IGNORECASE),
        "mass": re.compile(r"(?:Average )?Myocardial Mass\s*[:=]\s*([\d\.]+)\s*\(([\d\.]+)\)\s*g", re.DOTALL | re.IGNORECASE),
    }

    return patterns, patterns_measurement

def safe_extract(pattern, text):
    """Safely extract data using a regex pattern."""
    match = pattern.search(text)
    if match:
        return [group for group in match.groups() if group is not None]
    return []

def detect_format(text):
    """Detect the format of the report."""
    if re.search(r"\d+\.\s*(?:Morphology|Regurgitation|Flow Measurement|Ventricular Function)", text, re.DOTALL | re.IGNORECASE):
        return "compact"
    elif re.search(r"1\.\s*LV Function Measurement", text, re.DOTALL | re.IGNORECASE):
        return "sectioned"
    elif re.search(r"LV\s+RV", text, re.DOTALL | re.IGNORECASE):
        return "side_by_side"
    elif re.search(r"(?:LV|RV).*?EF.*?(?:LV|RV).*?EF", text, re.DOTALL | re.IGNORECASE):
        return "table"
    else:
        return "unknown"

def extract_data_compact(text, patterns, patterns_measurement):
    """Extract data from compact format reports."""
    results = {}

    ventricular_function = re.search(r"4\.\s*Ventricular Function(.*?)(?:\d+\.|$)", text, re.DOTALL | re.IGNORECASE)
    if ventricular_function:
        vf_text = ventricular_function.group(1)
        
        for ventricle in ['LV', 'RV']:
            for key, pattern in patterns_measurement.items():
                match = re.search(rf"{ventricle}\s+{key}\s*[:=]\s*([\d\.]+)(?:\s*\(([\d\.]+)\))?", vf_text, re.IGNORECASE)
                if match:
                    results[f'{ventricle} {key}'] = match.group(1)
                    if match.group(2):
                        results[f'{ventricle} {key}(Index)'] = match.group(2)

    bsa_match = re.search(r"BSA\s*[:=]\s*([\d\.]+)\s*m2", text, re.IGNORECASE)
    if bsa_match:
        results['BSA'] = bsa_match.group(1)

    delayed_enhancement = patterns["Delayed Enhancement"].search(text)
    if delayed_enhancement:
        results['Delayed Enhancement'] = delayed_enhancement.group(0)

    return results

def extract_data_table(text, patterns, patterns_measurement):
    """Extract data from table format reports."""
    results = {}

    for key, pattern in patterns.items():
        groups = safe_extract(pattern, text)
        if groups:
            results[key] = groups[0]

    lv_rv_pattern = re.compile(r"(?:LV|RV)\s*EF\s*([\d\.]+)%.*?(?:LV|RV)\s*EF\s*([\d\.]+)%.*?EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?(?:CO|cardiac output)\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?.*?(?:CO|cardiac output)\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?", re.DOTALL | re.IGNORECASE)
    
    lv_rv_match = lv_rv_pattern.search(text)
    if lv_rv_match:
        groups = lv_rv_match.groups()
        if len(groups) >= 18:
            if 'RV' in text.split('EF')[0].split('\n')[-1]:
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

    return results

def extract_data_side_by_side(text, patterns, patterns_measurement):
    """Extract data from side-by-side format reports."""
    results = {}

    for key, pattern in patterns.items():
        groups = safe_extract(pattern, text)
        if groups:
            results[key] = groups[0]

    lv_rv_pattern = re.compile(r"LV\s+RV.*?EF\s*([\d\.]+)%\s+EF\s*([\d\.]+)%.*?EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?\s+EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?\s+ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?\s+SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?.*?CO\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?\s+CO\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?", re.DOTALL | re.IGNORECASE)
    
    lv_rv_match = lv_rv_pattern.search(text)
    if lv_rv_match:
        groups = lv_rv_match.groups()
        if len(groups) >= 18:
            results['LV EF'], results['RV EF'] = groups[0], groups[1]
            results['LV EDV'], results['LV EDV(Index)'] = groups[2], groups[3]
            results['RV EDV'], results['RV EDV(Index)'] = groups[4], groups[5]
            results['LV ESV'], results['LV ESV(Index)'] = groups[6], groups[7]
            results['RV ESV'], results['RV ESV(Index)'] = groups[8], groups[9]
            results['LV SV'], results['LV SV(Index)'] = groups[10], groups[11]
            results['RV SV'], results['RV SV(Index)'] = groups[12], groups[13]
            results['LV CO'], results['LV CO(Index)'] = groups[14], groups[15]
            results['RV CO'], results['RV CO(Index)'] = groups[16], groups[17]

    return results

def extract_data_sectioned(text, patterns, patterns_measurement):
    """Extract data from sectioned format reports."""
    results = {}

    lv_section = re.search(r"1\.\s*LV Function Measurement.*?(?=2\.\s*RV Function Measurement|\Z)", text, re.DOTALL | re.IGNORECASE)
    rv_section = re.search(r"2\.\s*RV Function Measurement.*?(?=3\.|Forward Vol\.|\Z)", text, re.DOTALL | re.IGNORECASE)

    if lv_section:
        lv_text = lv_section.group(0)
        for key, pattern in patterns_measurement.items():
            match = pattern.search(lv_text)
            if match:
                results[f'LV {key}'] = match.group(1)
                if len(match.groups()) > 1 and match.group(2):
                    results[f'LV {key}(Index)'] = match.group(2)

    if rv_section:
        rv_text = rv_section.group(0)
        for key, pattern in patterns_measurement.items():
            match = pattern.search(rv_text)
            if match:
                results[f'RV {key}'] = match.group(1)
                if len(match.groups()) > 1 and match.group(2):
                    results[f'RV {key}(Index)'] = match.group(2)

    bsa_match = re.search(r"BSA\s*[:=]\s*([\d\.]+)\s*m2", text, re.IGNORECASE)
    if bsa_match:
        results['BSA'] = bsa_match.group(1)

    delayed_enhancement = patterns["Delayed Enhancement"].search(text)
    if delayed_enhancement:
        results['Delayed Enhancement'] = delayed_enhancement.group(0)

    return results

def process_data(df):
    patterns, patterns_measurement = define_patterns()
    all_results = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        try:
            text = row['value_source_value']
            format_type = detect_format(text)
            
            if format_type == "table":
                results = extract_data_table(text, patterns, patterns_measurement)
            elif format_type == "sectioned":
                results = extract_data_sectioned(text, patterns, patterns_measurement)
            elif format_type == "side_by_side":
                results = extract_data_side_by_side(text, patterns, patterns_measurement)
            elif format_type == "compact":
                results = extract_data_compact(text, patterns, patterns_measurement)
            else:
                results = extract_data_compact(text, patterns, patterns_measurement)  # Fallback to compact extraction

            results['Text'] = text
            results['pt_no'] = row['pt_no']
            results['Date'] = row['measurement_datetime']
            results['Code'] = row['procedure_source_code']
            results['Format'] = format_type
            all_results.append(results)
        except Exception as e:
            print(f"Error processing row {row['pt_no']}: {str(e)}")
            continue

    columns = ['pt_no', 'Date', 'Code', 'Format', 'Text', 'Delayed Enhancement', 'BSA',
           'LV EF', 'LV EDV', 'LV EDV(Index)', 'LV ESV', 'LV ESV(Index)',
           'LV SV', 'LV SV(Index)', 'LV CO', 'LV CO(Index)', 'LV mass', 'LV mass(Index)',
           'RV EF', 'RV EDV', 'RV EDV(Index)', 'RV ESV', 'RV ESV(Index)',
           'RV SV', 'RV SV(Index)', 'RV CO', 'RV CO(Index)', 'RV mass', 'RV mass(Index)']

    all_results_df = pd.DataFrame(all_results)
    all_results_df = all_results_df.reindex(columns=columns)

    # Convert 'Date' column to datetime and sort
    all_results_df['Date'] = pd.to_datetime(all_results_df['Date'])
    all_results_df = all_results_df.sort_values('Date')

    return all_results_df

def main():
    # Load data
    df = pd.read_csv(r'C:\Users\Roh\Documents\GitHub\TOF\mri\tof_mri.csv')

    # Process data
    all_results_df = process_data(df)

    # Save results
    all_results_df.to_csv('MRI_Regex_Improved.csv', index=False, encoding='utf-8-sig')

    # Print statistics
    print(f"Total number of records: {len(all_results_df)}")
    print(f"Number of records with RV EF: {all_results_df['RV EF'].notna().sum()}")
    print(f"Number of unique patients: {all_results_df['pt_no'].nunique()}")

    # Display a sample of the results
    print("\nSample of processed data:")
    print(all_results_df.head())

if __name__ == "__main__":
    main()