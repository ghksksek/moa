# omrlogic_drill.py

# ==============================================================================
# [정답 데이터베이스] 1회 ~ 8회 (각 40문항)
# ==============================================================================
# 현재는 테스트를 위해 [1, 2, 3, 4, 5] 패턴이 8번 반복되도록 설정했습니다.
# 실제 정답이 확정되면 아래 리스트를 실제 정답([1, 4, 3, ...])으로 교체하세요.
MOCK_ANSWERS = {}

# 1회 ~ 8회 자동 생성 (임시 데이터)
for i in range(1, 9):
    key = f"{i}회"
    # 40문항 예시: 1,2,3,4,5,1,2,3,4,5...
    MOCK_ANSWERS[key] = [1, 2, 3, 4, 5] * 8 

# 만약 특정 회차의 정답을 직접 넣으려면 아래처럼 덮어쓰면 됩니다.
# MOCK_ANSWERS["1회"] = [1, 5, 2, 3, 4, ... (40개 숫자)]


# ==============================================================================
# [핵심 로직] 메인 앱에서 호출하는 함수들
# ==============================================================================

def get_answer_key(exam_type, subject, year):
    """
    메인 앱에서 선택된 '회차(year)'에 해당하는 정답 리스트를 반환합니다.
    exam_type, subject 인자는 호환성을 위해 받지만, 내부적으로는 무시합니다.
    """
    # 딕셔너리에서 해당 회차(예: "1회")의 정답을 가져옵니다. 없으면 빈 리스트 반환.
    return MOCK_ANSWERS.get(year, [])


def grade_exam(user_answers, correct_answers):
    """
    채점 함수 (기존 로직 유지)
    user_answers: {1: 3, 2: 5, ...} 형태의 유저 답안 딕셔너리
    correct_answers: [1, 2, 3, ...] 형태의 정답 리스트
    """
    total_questions = len(correct_answers)
    
    # 정답 데이터가 없으면 0점 처리
    if total_questions == 0:
        return 0.0, []

    score_count = 0
    wrong_details = []

    for i in range(total_questions):
        q_num = i + 1              # 문항 번호 (1부터 시작)
        correct_ans = correct_answers[i]
        
        # 유저가 해당 번호를 풀었는지 확인 (안 풀었으면 None)
        user_ans = user_answers.get(q_num)

        # 정답 비교
        if user_ans == correct_ans:
            score_count += 1
        else:
            # 오답일 경우 상세 내용 기록
            wrong_details.append({
                "q_num": q_num,
                "user_ans": user_ans if user_ans else "미표기",
                "correct_ans": correct_ans
            })
            
    # 100점 만점 환산 점수 계산
    final_score = (score_count / total_questions) * 100
    
    return final_score, wrong_details


# ==============================================================================
# [호환성 유지용] 사용하지 않더라도 에러 방지를 위해 남겨둠
# ==============================================================================
def get_exam_types(): return ["모의고사"]
def get_subjects(exam_type): return ["신성우"]
def get_years(exam_type, subject): return list(MOCK_ANSWERS.keys())