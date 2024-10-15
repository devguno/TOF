import pandas as pd
import os

# 파일 경로
file_241014 = r"D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\Data_24_10_11.xlsx"
file_mri_report = r"D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\MRI_report_labeling.xlsx"

# 결과 파일 경로
result_file = r"D:\OneDrive\SNUH BMI Lab\TOF\VDysfunTof\mri\241014_processed.xlsx"

# 결과 파일을 저장할 디렉토리 확인 및 생성
result_dir = os.path.dirname(result_file)
if not os.path.exists(result_dir):
    os.makedirs(result_dir)
    print(f"디렉토리 생성됨: {result_dir}")

# Excel 파일 읽기
df_241014 = pd.read_excel(file_241014)
df_mri_report = pd.read_excel(file_mri_report)

# Ht와 Bwt의 첫 번째 값만 사용
df_241014['Ht'] = df_241014['Ht'].astype(str).str.split(',').str[0].str.strip()
df_241014['Bwt'] = df_241014['Bwt'].astype(str).str.split(',').str[0].str.strip()

# MRI 데이터와 원본 데이터 병합
merged_df = pd.merge(df_mri_report[['pt_no', 'Date', 'BSA']], df_241014, 
                     left_on='pt_no', right_on='Case No', how='right')

# 필요한 컬럼 선택 및 이름 변경
result_df = merged_df.copy()
result_df.rename(columns={'pt_no': 'mri_num', 'Date': 'mri_date', 'BSA_y': 'bsa'}, inplace=True)

# mri_num 계산
result_df['mri_num'] = result_df.groupby('Case No')['Case No'].transform('count')

# 날짜 형식 지정 및 NaN 값 처리
result_df['mri_date'] = pd.to_datetime(result_df['mri_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
result_df = result_df.fillna('')

# Case No와 mri_date로 중복 제거 (첫 번째 값 유지)
result_df = result_df.drop_duplicates(subset=['Case No', 'mri_date'], keep='first')

# Case No 기준으로 정렬
result_df = result_df.sort_values(['Case No', 'mri_date'])

# 결과를 새 파일로 저장
result_df.to_excel(result_file, index=False)

print(f"처리가 완료되었습니다. 결과가 {result_file}에 저장되었습니다.")
print(f"처리된 총 행 수: {len(result_df)}")

