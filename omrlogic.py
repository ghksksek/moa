# logic.py

# 3단계 계층 구조: 시험종류 -> 과목 -> 연도/회차 -> 정답리스트
EXAM_DB = {
    "LEET": {
        "언어이해": {
            "2024학년도": [1, 2, 3, 4, 5] * 6, # 30문항 예시
            "2023학년도": [5, 4, 3, 2, 1] * 6,
        },
        "추리논증": {
            "2024학년도": [1, 1, 1, 1, 1] * 8, # 40문항 예시
        }
    },
    "PSAT": {
        "언어논리": {
            "2023년 기출": [1, 2, 3, 4, 5] * 8, # 40문항
            "2022년 기출": [5, 4, 3, 2, 1] * 8,
        },
        "자료해석": {
            "2023년 기출": [1, 2, 3, 4, 5] * 8,
        },
        "상황판단": {
            "2023년 기출": [5, 5, 5, 5, 5] * 8,
        }
    },
    "모의고사": {
        "신성우": {
            "제1회 모의고사": [1, 2, 3, 4, 5] * 8,
            "제2회 모의고사": [1, 3, 5, 2, 4] * 8,
        }
    }
}

def get_exam_types():
    """시험 종류(LEET, PSAT, 모의고사) 반환"""
    return list(EXAM_DB.keys())

def get_subjects(exam_type):
    """선택된 시험 종류에 따른 과목 목록 반환"""
    if exam_type in EXAM_DB:
        return list(EXAM_DB[exam_type].keys())
    return []

def get_years(exam_type, subject):
    """선택된 과목에 따른 연도/회차 목록 반환"""
    if exam_type in EXAM_DB and subject in EXAM_DB[exam_type]:
        return list(EXAM_DB[exam_type][subject].keys())
    return []

def get_answer_key(exam_type, subject, year):
    """최종 정답 리스트 반환"""
    try:
        return EXAM_DB[exam_type][subject][year]
    except KeyError:
        return []

def grade_exam(user_answers, correct_answers):
    """채점 로직 (이전과 동일)"""
    total_questions = len(correct_answers)
    if total_questions == 0:
        return 0, []

    score_count = 0
    wrong_details = []

    for i in range(total_questions):
        q_num = i + 1
        user_ans = user_answers.get(q_num)
        correct_ans = correct_answers[i]

        if user_ans == correct_ans:
            score_count += 1
        else:
            wrong_details.append({
                "q_num": q_num,
                "user_ans": user_ans if user_ans else "미표기",
                "correct_ans": correct_ans
            })
            
    final_score = (score_count / total_questions) * 100
    return final_score, wrong_details