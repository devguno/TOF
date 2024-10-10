import re
import pandas as pd
from tqdm import tqdm

def define_patterns():
    """Define improved regex patterns for data extraction."""
    patterns = {
        "Delayed Enhancement": re.compile(r"No.*?abnormal delayed enhancement|No evidence of.*?delayed enhancement", re.IGNORECASE),
        "PR": re.compile(r"(No|Trivial|Mild|Moderate|Severe)\s+PR", re.IGNORECASE),
        "PR_fraction": re.compile(r"PR.*?regurgitation fraction.*?=.*?([\d\.]+)", re.DOTALL | re.IGNORECASE),
        "Lung_perfusion": re.compile(r"Lung perfusion.*?R\s*:\s*L\s*=\s*([\d\.]+)\s*%\s*:\s*([\d\.]+)\s*%", re.DOTALL | re.IGNORECASE),
        "BSA": re.compile(r"BSA\s*=\s*([\d\.]+)\s*m\^2", re.IGNORECASE),
    }

    patterns_measurement = {
        "EF": re.compile(r"Ejection Fraction\s*:\s*([\d\.]+)\s*%", re.DOTALL | re.IGNORECASE),
        "EDV": re.compile(r"End-Diastolic Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
        "ESV": re.compile(r"End-Systolic Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
        "SV": re.compile(r"Stroke Volume\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*ml", re.DOTALL | re.IGNORECASE),
        "CO": re.compile(r"Cardiac Output\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*[lL]/min", re.DOTALL | re.IGNORECASE),
        "MM": re.compile(r"Average Myocardial Mass\s*:\s*([\d\.]+)\s*\(([\d\.]+)\)\s*g", re.DOTALL | re.IGNORECASE),
    }

    patterns_table = {
        "EF": re.compile(r"LV\s+EF\s+([\d\.]+)%\s+RV\s+EF\s+([\d\.]+)%", re.DOTALL | re.IGNORECASE),
        "EDV": re.compile(r"EDV\s+([\d\.]+)ml\s*\(([\d\.]+)\)\s+EDV\s+([\d\.]+)ml\s*\(([\d\.]+)\)", re.DOTALL | re.IGNORECASE),
        "ESV": re.compile(r"ESV\s+([\d\.]+)ml\s*\(([\d\.]+)\)\s+ESV\s+([\d\.]+)ml\s*\(([\d\.]+)\)", re.DOTALL | re.IGNORECASE),
        "SV": re.compile(r"SV\s+([\d\.]+)ml\s*\(([\d\.]+)\)\s+SV\s+([\d\.]+)ml\s*\(([\d\.]+)\)", re.DOTALL | re.IGNORECASE),
        "CO": re.compile(r"CO\s+([\d\.]+)L/min\s*\(([\d\.]+)\)\s+CO\s+([\d\.]+)L/min\s*\(([\d\.]+)\)", re.DOTALL | re.IGNORECASE),
    }

    patterns_combined = {
        "EF": re.compile(r"EF\s+([\d\.]+)%\s+EF\s+([\d\.]+)%", re.DOTALL | re.IGNORECASE),
        "EDV": re.compile(r"EDV\s+([\d\.]+)ml\s*\(([\d\.]+)\)\s+EDV\s+([\d\.]+)ml\s*\(([\d\.]+)\)", re.DOTALL | re.IGNORECASE),
        "ESV": re.compile(r"ESV\s+([\d\.]+)ml\s*\(([\d\.]+)\)\s+ESV\s+([\d\.]+)ml\s*\(([\d\.]+)\)", re.DOTALL | re.IGNORECASE),
        "SV": re.compile(r"SV\s+([\d\.]+)ml\s*\(([\d\.]+)\)\s+SV\s+([\d\.]+)ml\s*\(([\d\.]+)\)", re.DOTALL | re.IGNORECASE),
        "CO": re.compile(r"CO\s+([\d\.]+)L/min\s*\(([\d\.]+)\)\s+CO\s+([\d\.]+)L/min\s*\(([\d\.]+)\)", re.DOTALL | re.IGNORECASE),
    }

    return patterns, patterns_measurement, patterns_table, patterns_combined

def safe_extract(pattern, text):
    """Safely extract data using a regex pattern."""
    match = pattern.search(text)
    if match:
        return [group for group in match.groups() if group is not None]
    return []

def detect_format(text):
    """Detect the format of the report."""
    if re.search(r"LV\s+EF.*RV\s+EF", text, re.DOTALL | re.IGNORECASE):
        return "table"
    elif re.search(r"1\.\s*LV Function Measurement", text, re.DOTALL | re.IGNORECASE):
        return "sectioned"
    elif re.search(r"LV\s+RV", text, re.DOTALL | re.IGNORECASE):
        return "combined"
    else:
        return "unknown"

def extract_data_combined(text, patterns, patterns_combined):
    """Extract data from combined format reports."""
    results = {}

    for key, pattern in patterns.items():
        groups = safe_extract(pattern, text)
        if groups:
            if key == "Lung_perfusion" and len(groups) >= 2:
                results["Lung_perfusion_Rt"] = groups[0]
                results["Lung_perfusion_Lt"] = groups[1]
            elif len(groups) >= 1:
                results[key] = groups[0]

    for key, pattern in patterns_combined.items():
        groups = safe_extract(pattern, text)
        if groups and len(groups) >= 4:
            results[f'LV {key}'] = groups[0]
            results[f'LV {key}(Index)'] = groups[1]
            results[f'RV {key}'] = groups[2]
            results[f'RV {key}(Index)'] = groups[3]

    return results

def extract_data_table(text, patterns, patterns_table):
    """Extract data from table format reports."""
    results = {}

    for key, pattern in patterns.items():
        groups = safe_extract(pattern, text)
        if groups:
            if key == "Lung_perfusion" and len(groups) >= 2:
                results["Lung_perfusion_Rt"] = groups[0]
                results["Lung_perfusion_Lt"] = groups[1]
            elif len(groups) >= 1:
                results[key] = groups[0]

    for key, pattern in patterns_table.items():
        groups = safe_extract(pattern, text)
        if groups:
            if key == 'EF':
                results[f'LV {key}'] = groups[0]
                results[f'RV {key}'] = groups[1]
            elif len(groups) >= 4:
                results[f'LV {key}'] = groups[0]
                results[f'LV {key}(Index)'] = groups[1]
                results[f'RV {key}'] = groups[2]
                results[f'RV {key}(Index)'] = groups[3]

    return results

def extract_data_sectioned(text, patterns, patterns_measurement):
    """Extract data from sectioned format reports."""
    results = {}

    for key, pattern in patterns.items():
        groups = safe_extract(pattern, text)
        if groups:
            if key == "Lung_perfusion" and len(groups) >= 2:
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
    patterns, patterns_measurement, patterns_table, patterns_combined = define_patterns()
    all_results = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        text = row['value_source_value']
        format_type = detect_format(text)
        
        if format_type == "combined":
            results = extract_data_combined(text, patterns, patterns_combined)
        elif format_type == "table":
            results = extract_data_table(text, patterns, patterns_table)
        elif format_type == "sectioned":
            results = extract_data_sectioned(text, patterns, patterns_measurement)
        else:
            results = extract_data_combined(text, patterns, patterns_combined)  # Fallback to combined extraction

        results['Text'] = text
        results['pt_no'] = row['pt_no']
        results['Date'] = row['measurement_datetime']
        results['Code'] = row['procedure_source_code']
        results['Format'] = format_type
        all_results.append(results)

    columns = ['pt_no', 'Date', 'Code', 'Format', 'Text', 'Delayed Enhancement', 'PR', 'PR_fraction', 'BSA',
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
    all_results_df.to_csv('MRI_Regex_Multi_Format_Improved.csv', index=False, encoding='utf-8-sig')

    # Print statistics
    print(f"Total number of records: {len(all_results_df)}")
    print(f"Number of records with RV EF: {all_results_df['RV EF'].notna().sum()}")
    print(f"Number of unique patients: {all_results_df['pt_no'].nunique()}")

    # Display a sample of the results
    print("\nSample of processed data:")
    print(all_results_df.head())

if __name__ == "__main__":
    main()