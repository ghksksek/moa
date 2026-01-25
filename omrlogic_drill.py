import pandas as pd
import uuid # 고유 ID 생성을 위해 필요
import csv
import os
from datetime import datetime

# omrlogic_drill.py

# ==========================================
# [정답 데이터베이스]
# 형식: "강사명": {"회차": {문제번호: 정답, ...}}
# ==========================================
ANSWER_DB = {
    "신성우": {
        "1회": {
            1: 3, 2: 4, 3: 1, 4: 3, 5: 3, 6: 2, 7: 3, 8: 1, 9: 3, 10: 2,
            11: 2, 12: 5, 13: 5, 14: 5, 15: 2, 16: 5, 17: 1, 18: 4, 19: 1, 20: 2,
            21: 2, 22: 4, 23: 4, 24: 3, 25: 4, 26: 4, 27: 4, 28: 2, 29: 5, 30: 4,
            31: 1, 32: 1, 33: 4, 34: 1, 35: 5, 36: 3, 37: 1, 38: 4, 39: 3, 40: 5
        },
        "2회": {
            1: 5, 2: 5, 3: 1, 4: 2, 5: 5, 6: 4, 7: 4, 8: 4, 9: 3, 10: 5,
            11: 4, 12: 3, 13: 5, 14: 1, 15: 3, 16: 1, 17: 5, 18: 2, 19: 3, 20: 3,
            21: 5, 22: 3, 23: 3, 24: 4, 25: 2, 26: 4, 27: 2, 28: 2, 29: 4, 30: 5,
            31: 5, 32: 3, 33: 3, 34: 5, 35: 1, 36: 1, 37: 3, 38: 5, 39: 4, 40: 3
        },
        "3회": {
            1: 1, 2: 1, 3: 5, 4: 2, 5: 4, 6: 4, 7: 5, 8: 2, 9: 5, 10: 1,
            11: 3, 12: 3, 13: 5, 14: 3, 15: 3, 16: 5, 17: 5, 18: 1, 19: 2, 20: 3,
            21: 5, 22: 1, 23: 1, 24: 2, 25: 4, 26: 3, 27: 5, 28: 3, 29: 4, 30: 4,
            31: 5, 32: 1, 33: 2, 34: 1, 35: 2, 36: 3, 37: 5, 38: 5, 39: 4, 40: 3
        },
        "4회": {
            1: 5, 2: 1, 3: 4, 4: 2, 5: 5, 6: 5, 7: 3, 8: 2, 9: 2, 10: 3,
            11: 4, 12: 2, 13: 3, 14: 2, 15: 2, 16: 5, 17: 2, 18: 2, 19: 1, 20: 2,
            21: 5, 22: 3, 23: 1, 24: 5, 25: 1, 26: 3, 27: 1, 28: 3, 29: 4, 30: 3,
            31: 4, 32: 3, 33: 1, 34: 1, 35: 2, 36: 3, 37: 5, 38: 1, 39: 5, 40: 3
        },
        "5회": {
            1: 5, 2: 3, 3: 3, 4: 4, 5: 4, 6: 3, 7: 1, 8: 5, 9: 1, 10: 3,
            11: 3, 12: 4, 13: 2, 14: 4, 15: 5, 16: 5, 17: 3, 18: 3, 19: 3, 20: 5,
            21: 4, 22: 4, 23: 2, 24: 3, 25: 4, 26: 2, 27: 4, 28: 1, 29: 3, 30: 4,
            31: 5, 32: 3, 33: 2, 34: 2, 35: 1, 36: 3, 37: 2, 38: 3, 39: 2, 40: 5
        },
        "6회": {
            1: 4, 2: 2, 3: 5, 4: 3, 5: 4, 6: 4, 7: 3, 8: 2, 9: 1, 10: 4,
            11: 3, 12: 4, 13: 1, 14: 4, 15: 1, 16: 5, 17: 2, 18: 3, 19: 4, 20: 5,
            21: 2, 22: 4, 23: 4, 24: 5, 25: 2, 26: 2, 27: 5, 28: 2, 29: 5, 30: 3,
            31: 3, 32: 4, 33: 3, 34: 2, 35: 4, 36: 3, 37: 2, 38: 5, 39: 3, 40: 2
        },
        "7회": {
            1: 5, 2: 3, 3: 5, 4: 5, 5: 2, 6: 2, 7: 5, 8: 3, 9: 1, 10: 5,
            11: 1, 12: 2, 13: 2, 14: 2, 15: 4, 16: 4, 17: 5, 18: 3, 19: 3, 20: 5,
            21: 5, 22: 4, 23: 1, 24: 5, 25: 2, 26: 3, 27: 4, 28: 3, 29: 4, 30: 5,
            31: 1, 32: 2, 33: 5, 34: 4, 35: 4, 36: 5, 37: 3, 38: 5, 39: 1, 40: 4
        },
        "8회": {
            1: 5, 2: 2, 3: 3, 4: 2, 5: 5, 6: 5, 7: 4, 8: 5, 9: 4, 10: 3,
            11: 2, 12: 1, 13: 3, 14: 3, 15: 2, 16: 4, 17: 4, 18: 5, 19: 5, 20: 3,
            21: 3, 22: 2, 23: 5, 24: 5, 25: 5, 26: 1, 27: 3, 28: 5, 29: 4, 30: 4,
            31: 1, 32: 4, 33: 3, 34: 3, 35: 5, 36: 3, 37: 2, 38: 1, 39: 2, 40: 3
        },
    }
}

def get_answer_key(exam_type, subject, round_num):
    """
    선택된 과목(subject)과 회차(round_num)에 맞는 정답 딕셔너리를 반환합니다.
    """
    if subject in ANSWER_DB and round_num in ANSWER_DB[subject]:
        return ANSWER_DB[subject][round_num]
    else:
        return {}

def grade_exam(user_answers, correct_answers):
    """
    사용자 답안과 정답을 비교하여 점수와 오답 상세 내역을 반환합니다.
    """
    if not correct_answers:
        return 0, []

    total_questions = len(correct_answers)
    correct_count = 0
    wrong_details = []

    # 문제 번호 순서대로 채점 (1번 ~ 40번)
    for q_num in sorted(correct_answers.keys()):
        correct_ans = correct_answers[q_num]
        user_ans = user_answers.get(q_num) # 사용자가 안 푼 문제는 None

        # 정답 비교
        if user_ans == correct_ans:
            correct_count += 1
        else:
            # 오답이거나 안 푼 경우
            wrong_details.append({
                "q_num": q_num,
                "user_ans": user_ans if user_ans else "미기입",
                "correct_ans": correct_ans
            })

    # 100점 만점 환산 (40문제 기준: 문제당 2.5점)
    score = (correct_count / total_questions) * 100
    
    return score, wrong_details

def save_exam_result(name, number, round_num, score, user_answers):
    """
    시험 결과를 CSV 파일에 누적 저장합니다.
    파일명: exam_results.csv
    저장 항목: [시간, 회차, 수험번호, 이름, 점수, 1번답, 2번답, ... 40번답]
    """
    file_name = "exam_results.csv"
    
    # 1. 저장할 데이터 준비
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 기본 정보
    row_data = [now, round_num, number, name, score]
    
    # 1번부터 40번까지 답안을 순서대로 리스트에 추가 (안 푼 건 빈칸 처리)
    for q in range(1, 41):
        ans = user_answers.get(q, "") # 값이 없으면 공백
        row_data.append(ans)

    # 2. 파일이 없으면 헤더(제목 줄) 먼저 만들기
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        
        # 파일이 처음 생성되는 거라면 헤더 작성
        if not file_exists:
            header = ['타임스탬프', '회차', '수험번호', '이름', '점수'] + [f'Q{i}' for i in range(1, 41)]
            writer.writerow(header)
        
        # 데이터 한 줄 추가
        writer.writerow(row_data)
QNA_FILE = "qna_db.csv"

def load_qna_data():
    """CSV 파일에서 질의응답 데이터를 읽어옵니다."""
    if not os.path.isfile(QNA_FILE):
        return []
    
    # pandas를 쓰지 않고 csv 모듈로 읽기 (가볍게 처리)
    qna_list = []
    with open(QNA_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            qna_list.append(row)
    return qna_list

def save_question(round_num, q_num, content, user_number, user_name):
    """새로운 질문을 저장합니다."""
    file_exists = os.path.isfile(QNA_FILE)
    
    # 고유 ID 생성 (답변 달 때 찾기 위해)
    q_id = str(uuid.uuid4())[:8] 
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(QNA_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['id', 'timestamp', 'round', 'q_num', 'u_number', 'u_name', 'question', 'answer', 'ans_time']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        writer.writerow({
            'id': q_id,
            'timestamp': now,
            'round': round_num,
            'q_num': q_num,
            'u_number': user_number,
            'u_name': user_name,
            'question': content,
            'answer': '',     # 답변은 비워둠
            'ans_time': ''
        })

def save_answer(q_id, answer_text):
    """관리자가 단 답변을 해당 질문에 업데이트합니다."""
    # CSV는 수정이 불편하므로, 다 읽어서 메모리에서 수정 후 다시 씁니다.
    all_data = load_qna_data()
    updated = False
    
    for row in all_data:
        if row['id'] == q_id:
            row['answer'] = answer_text
            row['ans_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = True
            break
            
    if updated:
        with open(QNA_FILE, mode='w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['id', 'timestamp', 'round', 'q_num', 'u_number', 'u_name', 'question', 'answer', 'ans_time']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
    return updated
        