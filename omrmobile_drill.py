import streamlit as st
import omrlogic_drill as omrlogic

# [회차별 수정사항 데이터베이스]
REVISIONS_DB = {
    "1회": "• 12번 문제: 선지 ④번 '적절한' -> '적절하지 않은'으로 수정<br>• 20번 문제: 지문 세 번째 줄 오타 수정",
    "2회": "• 5번 문제: 복수 정답 인정 (1번, 3번)",
    "3회": "수정사항이 없습니다."
}

# [회차별 검토의견 데이터베이스]
COMMENTS_DB = {
    "1회": "• 난이도: 중상<br>• 법률 지문의 길이가 길어 시간 배분에 유의해야 함.<br>• 15번 문항의 논리 구조가 매우 우수함.",
    "2회": "• 난이도: 상<br>• 논리퀴즈 유형이 다수 출제되어 체감 난이도가 높음.",
    "3회": "등록된 검토의견이 없습니다."
}

# --- 페이지 설정 ---
st.set_page_config(page_title="모바일 OMR", layout="centered")

# --- CSS 스타일 ---
st.markdown("""
<style>
    /* 1. 기본 리셋 */
    * { box-sizing: border-box !important; min-width: 0 !important; }

    /* [기본] 첫 화면은 넓게(450px) */
    .block-container {
        max-width: 450px !important; width: 100% !important;
        padding: 10px 5px !important; margin: 0 auto !important;
    }

/* 2. 버튼 스타일 */
    /* (1) 일반 버튼 */
    .stButton > button {
        border: 1px solid #cccccc !important; 
        color: #666 !important;
        background-color: #fff !important;
        margin-top: 2px !important; 
        width: 100%;
        font-weight: bold;
    }
    .stButton > button:hover {
        border: 1px solid #999 !important;
        color: #333 !important;
    }

    /* (2) 시험 시작 버튼 (Primary Type) */
    .stButton > button[kind="primary"] {
        border: 2px solid #333 !important;
        background-color: #333 !important;
        color: white !important;
        margin-top: 5px !important; 
    }
    .stButton > button[kind="primary"]:hover {
        background-color: black !important;
        border-color: black !important;
    }

    /* (3) [수정됨] 채점하기 버튼 (Form Submit) - 가장 강력하게 적용 */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #333 !important;
        border: 2px solid #333 !important;
        color: white !important;
        margin-top: 5px !important;
        font-weight: bold !important;
    }
    
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: black !important;
        border-color: black !important;
        color: white !important;
    }
    
    div[data-testid="stFormSubmitButton"] button:active,
    div[data-testid="stFormSubmitButton"] button:focus {
        background-color: #333 !important;
        border-color: #333 !important;
        color: white !important;
    }

    /* 3. 정보 박스 */
    .info-box {
        border: 1px solid #ddd !important;
        background-color: #f9f9f9 !important; 
        border-radius: 5px !important;
        padding: 15px !important;
        margin-top: 2px !important;
        margin-bottom: 2px !important;
        color: #444 !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    /* 4. 컬럼 레이아웃 */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important; flex-wrap: nowrap !important; width: 100% !important; gap: 0 !important;
    }
    /* 1번 컬럼 (문번) */
    div[data-testid="column"]:nth-of-type(1) {
        overflow: hidden !important; padding: 0 !important; display: flex; justify-content: center; align-items: center;
    }
    /* 2번 컬럼 (답란): 수평/수직 중앙 정렬 */
    div[data-testid="column"]:nth-of-type(2) {
        width: auto !important; 
        padding-left: 2px !important; 
        display: flex; 
        align-items: center; 
        justify-content: center !important;
    }
    /* 2번 컬럼 내부 수직 블록 정렬 강제 */
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] {
        align-items: center !important;
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
    }
    div[data-testid="column"]:nth-of-type(3) {
        width: auto !important; padding:0 !important; display: flex; align-items: center;
    }

    /* 5. 메인 컨테이너 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 2px solid #333 !important; border-radius: 0px !important; padding: 0 !important; width: 100% !important;
        background: linear-gradient(to right, #f0f2f6 0%, #f0f2f6 35px, #333 35px, #333 37px, #ffffff 37px, #ffffff 100%) !important;
    }

    /* 6. 라디오 버튼 (OMR) */
    div[role="radiogroup"] input[type="radio"], div[role="radiogroup"] label > div:first-child { display: none !important; }
    
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        border: 2px solid #ea5656 !important; border-radius: 50% !important;
        width: clamp(16px, 6vw, 24px) !important; height: clamp(22px, 8vw, 30px) !important;
        display: flex; justify-content: center; align-items: center;
        font-size: clamp(10px, 4vw, 13px) !important; font-weight: bold !important;
        color: #ea5656 !important; background: white !important; margin: 0 auto !important;
    }
    
    div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {
        background-color: black !important; 
        border-color: black !important; 
        color: black !important; 
    }
    
    /* OMR 버튼 그룹 정렬 및 크기 제한 */
    div[role="radiogroup"] { 
            display: flex; 
            justify-content: space-between; 
            width: 100% !important; 
            padding: 4px 0 !important; 
            margin-top: -4px !important; 
            max-width: 240px !important; 
            margin: 0 auto !important;   
    }
    div[role="radiogroup"] label { flex: 1; display: flex; justify-content: center; margin: 0 !important; padding: 0 !important; }

    /* 7. UI 정리 */
    div[data-testid="stForm"] { border: none !important; padding: 0 !important; width: 100% !important; }
    
    /* 폼 내부 간격 좁히기 */
    div[data-testid="stForm"] > div[data-testid="stVerticalBlock"] {
        gap: 0.3rem !important; 
    }

    .q-num-box { 
        font-weight: 800; text-align: center; color: #333; font-size: 13px; 
        display: flex; align-items: center; justify-content: center; height: 30px; margin-top: 6px;
    }
    .header-box { font-weight: bold; text-align: center; color: #333; font-size: 13px; padding: 8px 0; white-space: nowrap; }
    
    /* [수정됨] 점선 구분선 스타일: 여백을 0으로 만들어 간격 축소 */
    .separator-line { 
        position: relative; 
        width: 100%; 
        border-top: 1px dashed #bbb; 
        height: 1px; 
        /* [핵심] 음수 마진으로 위아래 공백을 상쇄시킴 */
        margin-top: -8px !important;    
        margin-bottom: -18px !important; 
        z-index: 0; /* 다른 요소 뒤로 숨지 않도록 */
    }
    
    .start-title { text-align: center; color: #333; margin-bottom: 20px; font-size: 28px !important; font-weight: 800; }
    .info-text { text-align: center; color: #666; font-size: 13px; line-height: 1.6; margin-top: 15px; margin-bottom: 5px; word-break: keep-all; }
    
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stAppDeployButton {display:none;} div[data-testid="stToolbar"] {display:none;}
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a { display: none !important; pointer-events: none !important; }

    /* 8. 구분선 */
    hr { margin-top: 0px !important; margin-bottom: 20px !important; border-color: #e0e0e0 !important; }

    /* 9. 힌트 숨기기 */
    div[data-testid="InputInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 세션 초기화 ---
if 'exam_started' not in st.session_state: st.session_state['exam_started'] = False
if 'user_answers' not in st.session_state: st.session_state['user_answers'] = {}
if 'submitted' not in st.session_state: st.session_state['submitted'] = False
if 'show_revisions' not in st.session_state: st.session_state['show_revisions'] = False
if 'show_comments' not in st.session_state: st.session_state['show_comments'] = False

# ==============================================================================
# [화면 1] 설정
# ==============================================================================
if not st.session_state['exam_started']:
    st.markdown("<h1 class='start-title'>26년 신성우 모의고사</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        # 1. 회차 선택
        round_options = [f"{i}회" for i in range(1, 9)]
        selected_round = st.selectbox("회차", round_options)
        
        # [기능 1] 수정사항 보기
        if st.button("수정사항 보기", use_container_width=True):
            st.session_state['show_revisions'] = not st.session_state['show_revisions']
        
        if st.session_state['show_revisions']:
            rev_content = REVISIONS_DB.get(selected_round, "등록된 수정사항이 없습니다.")
            rev_content = rev_content.replace("\n", "<br>")
            html_content = f'<div class="info-box"><strong style="display:block; margin-bottom:8px; color:#d63031;">📢 [{selected_round} 정오표]</strong>{rev_content}</div>'
            st.markdown(html_content, unsafe_allow_html=True)

        # [기능 2] 검토의견 보기
        if st.button("검토의견 보기", use_container_width=True):
            st.session_state['show_comments'] = not st.session_state['show_comments']
            
        if st.session_state['show_comments']:
            cmt_content = COMMENTS_DB.get(selected_round, "등록된 검토의견이 없습니다.")
            cmt_content = cmt_content.replace("\n", "<br>")
            html_content_cmt = f'<div class="info-box"><strong style="display:block; margin-bottom:8px; color:#0984e3;">💡 [{selected_round} 검토의견]</strong>{cmt_content}</div>'
            st.markdown(html_content_cmt, unsafe_allow_html=True)

        st.divider()
        
        # 2. 수험번호와 성명
        user_number = st.text_input("수험번호", placeholder="숫자만 입력하세요")
        user_name = st.text_input("성명", placeholder="문자만 입력하세요")
        
        st.markdown("""
            <div class='info-text'>
            수험번호와 성명은 공개되지 않습니다.<br>
            답안을 제출하면 통계를 볼 수 있습니다.
            </div>
        """, unsafe_allow_html=True)
        
        # [기능 3] 시험 시작
        if st.button("시험 시작", type="primary", use_container_width=True):
            if not user_name or not user_number:
                st.warning("수험번호와 성명을 모두 입력하세요.")
            elif not user_number.isdigit():
                st.error("🚨 수험번호는 숫자만 입력 가능합니다.")
            else:
                st.session_state.update({
                    'info_type': "모의고사", 
                    'info_subject': "신성우", 
                    'info_year': selected_round,
                    'info_number': user_number, 
                    'info_name': user_name,
                    'exam_started': True, 
                    'user_answers': {}, 
                    'submitted': False
                })
                st.rerun()

        # 통계 및 질의응답
        c1, space, c2 = st.columns([1, 0.05, 1]) 
        
        with c1:
            if st.button("시험 통계 보기", use_container_width=True):
                st.toast("🚧 통계 기능은 준비 중입니다.")
        
        with c2:
            if st.button("질의 응답", use_container_width=True):
                st.toast("🚧 질의응답 게시판은 준비 중입니다.")

# ==============================================================================
# [화면 2] OMR 작성
# ==============================================================================
else:
    # [화면 2 전용] 폭 300px로 좁게 설정
    st.markdown("""
    <style>
        .block-container {
            max-width: 300px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    e_subj = st.session_state['info_subject']
    u_name = st.session_state['info_name']
    u_round = st.session_state['info_year']
    
    st.markdown(f"**{u_round}** | {u_name}")

    correct_answers = omrlogic.get_answer_key(st.session_state['info_type'], e_subj, u_round)
    total_q = len(correct_answers)

    if total_q > 0:
        with st.form("omr_form", border=False):
            with st.container(border=True):
                h1, h2 = st.columns([2.5, 7.5]) 
                with h1: st.markdown("<div class='header-box'>문번</div>", unsafe_allow_html=True)
                with h2: st.markdown("<div class='header-box'>답 란&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>", unsafe_allow_html=True)
                st.markdown("<div style='border-top: 2px solid #333; width:100%; line-height:0;'>&nbsp;</div>", unsafe_allow_html=True)

                for q in range(1, total_q + 1):
                    # 구분선: CSS 수정으로 margin 0이 되어 간격 좁아짐
                    if q > 1 and (q - 1) % 5 == 0:
                        st.markdown("<div class='separator-line'></div>", unsafe_allow_html=True)

                    r1, r2 = st.columns([2.5, 7.5])
                    with r1: st.markdown(f"<div class='q-num-box'>{q}</div>", unsafe_allow_html=True)
                    with r2:
                        val = st.radio(f"q_{q}", [1,2,3,4,5], horizontal=True, label_visibility="collapsed", key=f"q_{q}", index=None)
                        st.session_state['user_answers'][q] = val
            
            if st.form_submit_button("채점하기", type="primary", use_container_width=True):
                st.session_state['submitted'] = True
                st.rerun()
    else:
        st.error(f"'{u_round}'에 대한 정답 데이터가 없습니다.")
        if st.button("돌아가기"): st.session_state['exam_started'] = False; st.rerun()

    if st.session_state['submitted']:
        st.divider()
        score, wrong_details = omrlogic.grade_exam(st.session_state['user_answers'], correct_answers)
        st.info(f"점수: **{score:.1f}점**")
        if wrong_details:
            st.write(f"오답: {len(wrong_details)}개")
            for item in wrong_details:
                st.markdown(f"<div style='background:#fff5f5; padding:5px; margin-bottom:5px;'><b>{item['q_num']}번</b>: <span style='color:red'>{item['user_ans']}</span> / <span style='color:blue'>{item['correct_ans']}</span></div>", unsafe_allow_html=True)
        else:
            st.success("만점입니다!")
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("다시 풀기", use_container_width=True): st.session_state['user_answers'] = {}; st.session_state['submitted'] = False; st.rerun()
        with c2:
            if st.button("홈으로", use_container_width=True): st.session_state['exam_started'] = False; st.rerun()