import pandas as pd
import os

# 파일 경로
file_241014 = r"D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\241014.xlsx"
file_mri_report = r"D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\MRI_report_labeling.xlsx"

# 결과 파일 경로
result_file = r"D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\241014_processed.xlsx"

# Excel 파일 읽기
df_241014 = pd.read_excel(file_241014)
df_mri_report = pd.read_excel(file_mri_report)

# 'Case No'와 'pt_no'를 기준으로 데이터 그룹화
grouped = df_mri_report.groupby('pt_no')

# 새로운 컬럼 초기화
df_241014['mri_num'] = 0
df_241014['mri_date'] = ''
df_241014['bsa'] = ''

# 각 행에 대해 처리
for index, row in df_241014.iterrows():
    case_no = row['Case No']
    if case_no in grouped.groups:
        group = grouped.get_group(case_no)
        
        # mri_num 계산
        mri_num = len(group)
        
        # mri_date와 bsa 문자열 생성
        mri_dates = ','.join(group['Date'].astype(str))
        bsas = ','.join(group['BSA'].astype(str))
        
        # 새 컬럼에 값 할당
        df_241014.at[index, 'mri_num'] = mri_num
        df_241014.at[index, 'mri_date'] = mri_dates
        df_241014.at[index, 'bsa'] = bsas

# 결과를 새 파일로 저장
df_241014.to_excel(result_file, index=False)

print(f"처리가 완료되었습니다. 결과가 {result_file}에 저장되었습니다.")