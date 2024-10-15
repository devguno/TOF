import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 읽기
vdt_cohort = pd.read_csv(r'D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\vdt_cohort.csv')

# Excel 파일 읽기
processed_data = pd.read_excel(r'D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\241014_processed.xlsx')

# 'pt_no'를 기준으로 두 데이터프레임 병합
merged_data = pd.merge(processed_data, vdt_cohort[['pt_no', 'gender_source_value', 'year_of_birth']], 
                       left_on='Case No', right_on='pt_no', how='left')

# 'DOB' 컬럼에서 년도 추출
merged_data['DOB_year'] = pd.to_datetime(merged_data['DOB']).dt.year

# 년도 일치 여부 확인 및 차이 계산
merged_data['year_match'] = merged_data['DOB_year'] == merged_data['year_of_birth']
merged_data['year_difference'] = merged_data['DOB_year'] - merged_data['year_of_birth']

# 일치하는 데이터의 비율 계산
match_ratio = merged_data['year_match'].mean() * 100

print(f"DOB와 year_of_birth가 일치하는 데이터의 비율: {match_ratio:.2f}%")

# 불일치하는 경우 분석
mismatched_data = merged_data[~merged_data['year_match']]
year_diff_counts = mismatched_data['year_difference'].value_counts().sort_index()

print("\n연도 차이 분포:")
print(year_diff_counts)



# 결과를 새 Excel 파일로 저장
output_path = r'D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\241014_processed_with_gender_and_year_analysis.xlsx'
merged_data.to_excel(output_path, index=False)

print(f"\n결과가 {output_path}에 저장되었습니다.")