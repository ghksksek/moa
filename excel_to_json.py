import pandas as pd
import json
import os

# 1. 엑셀 파일 읽기
excel_file = 'answers.xlsx'

if not os.path.exists(excel_file):
    print(f"❌ '{excel_file}' 파일이 없습니다. 같은 폴더에 엑셀 파일을 넣어주세요.")
    exit()

print("📂 엑셀 파일을 읽는 중...")
try:
    df = pd.read_excel(excel_file)
except Exception as e:
    print(f"❌ 엑셀 읽기 실패: {e}")
    print("👉 'pip install pandas openpyxl' 을 설치했는지 확인하세요.")
    exit()

# 2. 데이터 변환 (Nested Dictionary 구조로 변경)
# 목표 구조: { "2017 (추리)": { "1": { "ans": "3", "exp": "해설..." } } }

data = {}

for index, row in df.iterrows():
    # 엑셀의 각 열 데이터 가져오기 (비어있으면 무시)
    if pd.isna(row['연도_과목']) or pd.isna(row['번호']):
        continue
        
    year_key = str(row['연도_과목']).strip() # 예: 2017 (추리)
    q_num = str(int(row['번호']))            # 예: 1 (정수로 변환 후 문자열)
    ans = str(row['정답']).strip() if not pd.isna(row['정답']) else "?"
    exp = str(row['해설']).strip() if not pd.isna(row['해설']) else ""

    # 1. 연도 키가 없으면 생성
    if year_key not in data:
        data[year_key] = {}
    
    # 2. 해당 번호에 정답/해설 넣기
    data[year_key][q_num] = {
        "ans": ans,
        "exp": exp
    }

# 3. JSON 파일로 저장
output_file = 'answers.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 변환 완료! '{output_file}' 파일이 생성되었습니다.")