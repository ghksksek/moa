import pandas as pd
import json
import os

def excel_to_json(input_file='data.xlsx', output_file='answers.json'):
    # 1. 엑셀 파일 읽기
    if not os.path.exists(input_file):
        print(f"오류: '{input_file}' 파일이 없습니다.")
        return

    try:
        # 모든 데이터를 문자로 읽어서 포맷 깨짐 방지
        df = pd.read_excel(input_file, dtype=str)
        print("엑셀 파일을 성공적으로 읽었습니다.")
    except Exception as e:
        print(f"엑셀 파일 읽기 실패: {e}")
        return

    # 2. 데이터 변환 로직
    result = {}
    
    # 과목명 매핑 (엑셀에 '추리논증'이라 써도 '추리'로 변환)
    subject_map = {
        "추리논증": "추리",
        "추리": "추리",
        "언어이해": "언어",
        "언어": "언어"
    }

    for index, row in df.iterrows():
        # 결측값 처리
        if pd.isna(row['연도']) or pd.isna(row['과목']) or pd.isna(row['번호']):
            continue

        year = row['연도'].strip()
        raw_subject = row['과목'].strip()
        number = row['번호'].strip()
        # 정답은 소수점(.0)이 붙을 수 있으므로 처리
        ans = row['정답'].strip().split('.')[0] if not pd.isna(row['정답']) else "?"

        # 과목명 변환 (매핑표에 없으면 그대로 사용)
        subject = subject_map.get(raw_subject, raw_subject)

        # [핵심] 키 생성: "2024 (추리)" 형식
        key_name = f"{year} ({subject})"

        # 구조 만들기
        if key_name not in result:
            result[key_name] = {}

        result[key_name][number] = {
            "ans": ans
            # 나중에 해설이 필요하면 여기에 추가: "desc": row['해설']
        }

    # 3. JSON 파일로 저장
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"변환 완료! '{output_file}' 파일이 생성되었습니다.")
        print(f"생성된 키 예시: {list(result.keys())[:3]}") # 확인용 출력
    except Exception as e:
        print(f"JSON 저장 실패: {e}")

if __name__ == "__main__":
    # 라이브러리 설치 필요: pip install pandas openpyxl
    excel_to_json()