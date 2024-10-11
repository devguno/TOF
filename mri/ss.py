import re
import pandas as pd
from tqdm import tqdm

def define_patterns():
    """Define improved regex patterns for data extraction."""
    patterns = {
        "Delayed Enhancement": re.compile(r"No.*?(?:abnormal delayed enhancement|evidence of.*?delayed enhancement|evidence of myocardiac infarction)", re.IGNORECASE),
        "PR": re.compile(r"(No|Trivial|Mild|Moderate to severe|Moderate|Severe)\s+PR", re.IGNORECASE),
        "PR_fraction": re.compile(r"(?:PR|MPA RF|RPA\+LPA RF|regurgitation fraction).*?=.*?(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)", re.DOTALL | re.IGNORECASE),
        "Lung_perfusion": re.compile(r"Lung perfusion.*?R\s*:\s*L\s*=\s*([\d\.]+)\s*%\s*:\s*([\d\.]+)\s*%", re.DOTALL | re.IGNORECASE),
        "BSA": re.compile(r"(?:BSA|Body surface area)\s*=\s*([\d\.]+)\s*(?:m\^2|M2)", re.IGNORECASE),
        "TR": re.compile(r"(No|Trivial|Mild|Moderate to severe|Moderate|Severe)\s+TR", re.IGNORECASE),
    }

    patterns_measurement = {
        "EF": re.compile(r"EF\s*([\d\.]+)%", re.DOTALL | re.IGNORECASE),
        "EDV": re.compile(r"EDV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?", re.DOTALL | re.IGNORECASE),
        "ESV": re.compile(r"ESV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?", re.DOTALL | re.IGNORECASE),
        "SV": re.compile(r"SV\s*([\d\.]+)(?:\s*ml)?(?:\s*\(([\d\.]+)\))?", re.DOTALL | re.IGNORECASE),
        "CO": re.compile(r"(?:CO|cardiac output)\s*([\d\.]+)(?:\s*L/min)?(?:\s*\(([\d\.]+)\))?", re.DOTALL | re.IGNORECASE),
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
    if re.search(r"(?:LV|RV).*?EF.*?(?:LV|RV).*?EF", text, re.DOTALL | re.IGNORECASE):
        return "table"
    elif re.search(r"1\.\s*LV Function Measurement", text, re.DOTALL | re.IGNORECASE):
        return "sectioned"
    elif re.search(r"LV\s+RV", text, re.DOTALL | re.IGNORECASE):
        return "side_by_side"
    else:
        return "unknown"

def extract_data_table(text, patterns, patterns_measurement):
    """Extract data from table format reports."""
    results = {}

    for key, pattern in patterns.items():
        groups = safe_extract(pattern, text)
        if groups:
            if key == "PR_fraction" and len(groups) >= 3:
                results["PR_fraction_numerator"] = groups[0]
                results["PR_fraction_denominator"] = groups[1]
                results["PR_fraction_value"] = groups[2]
            elif key == "Lung_perfusion" and len(groups) >= 2:
                results["Lung_perfusion_Rt"] = groups[0]
                results["Lung_perfusion_Lt"] = groups[1]
            elif len(groups) >= 1:
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
            if key == "PR_fraction" and len(groups) >= 3:
                results["PR_fraction_numerator"] = groups[0]
                results["PR_fraction_denominator"] = groups[1]
                results["PR_fraction_value"] = groups[2]
            elif key == "Lung_perfusion" and len(groups) >= 2:
                results["Lung_perfusion_Rt"] = groups[0]
                results["Lung_perfusion_Lt"] = groups[1]
            elif len(groups) >= 1:
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

    for key, pattern in patterns.items():
        groups = safe_extract(pattern, text)
        if groups:
            if key == "PR_fraction" and len(groups) >= 3:
                results["PR_fraction_numerator"] = groups[0]
                results["PR_fraction_denominator"] = groups[1]
                results["PR_fraction_value"] = groups[2]
            elif key == "Lung_perfusion" and len(groups) >= 2:
                results["Lung_perfusion_Rt"] = groups[0]
                results["Lung_perfusion_Lt"] = groups[1]
            elif len(groups) >= 1:
                results[key] = groups[0]

    lv_section = re.search(r"1\.\s*LV Function Measurement.*?(?=2\.\s*RV Function Measurement|\Z)", text, re.DOTALL)
    rv_section = re.search(r"2\.\s*RV Function Measurement.*?(?=3\.|Forward Vol\.|\Z)", text, re.DOTALL)

    if lv_section:
        for key, pattern in patterns_measurement.items():
            groups = safe_extract(pattern, lv_section.group(0))
            if groups:
                results[f'LV {key}'] = groups[0]
                if len(groups) > 1:
                    results[f'LV {key}(Index)'] = groups[1]

    if rv_section:
        for key, pattern in patterns_measurement.items():
            groups = safe_extract(pattern, rv_section.group(0))
            if groups:
                results[f'RV {key}'] = groups[0]
                if len(groups) > 1:
                    results[f'RV {key}(Index)'] = groups[1]

    return results

def process_data(df):
    """Process the data and return the final DataFrame."""
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
            else:
                results = extract_data_table(text, patterns, patterns_measurement)  # Fallback to table extraction

            results['Text'] = text
            results['pt_no'] = row['pt_no']
            results['Date'] = row['measurement_datetime']
            results['Code'] = row['procedure_source_code']
            results['Format'] = format_type
            all_results.append(results)
        except Exception as e:
            print(f"Error processing row {row['pt_no']}: {str(e)}")
            continue

    columns = ['pt_no', 'Date', 'Code', 'Format', 'Text', 'Delayed Enhancement', 'PR', 
               'PR_fraction_numerator', 'PR_fraction_denominator', 'PR_fraction_value', 'BSA',
               'Lung_perfusion_Rt', 'Lung_perfusion_Lt',
               'LV EF', 'LV EDV', 'LV EDV(Index)', 'LV ESV', 'LV ESV(Index)',
               'LV SV', 'LV SV(Index)', 'LV CO', 'LV CO(Index)', 'LV MM', 'LV MM(Index)',
               'RV EF', 'RV EDV', 'RV EDV(Index)', 'RV ESV', 'RV ESV(Index)',
               'RV SV', 'RV SV(Index)', 'RV CO', 'RV CO(Index)', 'RV MM', 'RV MM(Index)']

    all_results_df = pd.DataFrame(all_results)
    all_results_df = all_results_df.reindex(columns=columns)

    # Convert 'Date' column to datetime and sort
    all_results_df['Date'] = pd.to_datetime(all_results_df['Date'])
    all_results_df = all_results_df.sort_values('Date')

    return all_results_df

def main():
    # Load data
    df = pd.read_csv(r'C:\github\TOF\mri\tof_mri.csv')

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