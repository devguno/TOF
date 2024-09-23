import pandas as pd
import re

# CSV 파일 불러오기 (인코딩을 ISO-8859-1로 변경)
df = pd.read_csv(r'C:\github\TOF\mri\MRI_Regex_updated.csv', encoding='ISO-8859-1')

# BSA 값을 추출하는 함수 정의 (정규 표현식을 사용하여 Text 컬럼에서 BSA 값 추출)
def extract_bsa(text):
    # 정규 표현식으로 "BSA : 값 m2" 패턴 추출
    match = re.search(r'BSA\s*:\s*([\d.]+)\s*m2', str(text))
    if match:
        return float(match.group(1))  # 매칭된 BSA 값을 float으로 반환
    return None  # 값이 없으면 None 반환

# Text 컬럼에서 BSA 값을 추출하여 새로운 BSA 컬럼 생성
df['BSA'] = df['Text'].apply(extract_bsa)

# 결과 저장
df.to_csv(r'C:\github\TOF\mri\MRI_Regex_with_BSA.csv', index=False, encoding='utf-8')

print("BSA 추출 완료 및 MRI_Regex_with_BSA.csv에 저장되었습니다.")
