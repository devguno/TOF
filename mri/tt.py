import pandas as pd

# CSV 파일 불러오기
vdtof_mri = pd.read_csv(r'C:\Users\iamgu\Documents\GitHub\TOF\mri\vdtof_mri.csv')
mri_regex = pd.read_csv(r'C:\Users\iamgu\Documents\GitHub\TOF\mri\MRI_Regex.csv')

# measurement_datetime을 datetime 형식으로 변환 후 날짜 정보만 추출
vdtof_mri['measurement_datetime'] = pd.to_datetime(vdtof_mri['measurement_datetime']).dt.date
mri_regex['measurement_datetime'] = pd.to_datetime(mri_regex['measurement_datetime']).dt.date

# measurement_datetime과 pt_no를 기준으로 데이터 매칭
merged_df = pd.merge(
    mri_regex,
    vdtof_mri[['measurement_datetime', 'pt_no', 'measurement_datetime_for_weight', 'value_for_weight', 'measurement_datetime_for_height', 'value_for_height']],
    on=['measurement_datetime', 'pt_no'],
    how='left'  # mri_regex의 모든 데이터를 유지하고 vdtof_mri에서 일치하는 데이터를 가져옴
)

# 결과 저장
merged_df.to_csv(r'C:\Users\iamgu\Documents\GitHub\TOF\mri\MRI_Regex_updated.csv', index=False, encoding='utf-8')

print("데이터 매칭 완료 및 MRI_Regex_updated.csv에 저장되었습니다.")
