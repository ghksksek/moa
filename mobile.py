import streamlit as st
import logic

# --- 페이지 설정 ---
st.set_page_config(page_title="모바일 OMR", layout="centered")

# --- CSS 스타일 (이전과 동일한 디자인 유지) ---
st.markdown("""
<style>
    /* 1. 라디오 버튼 (타원형) */
    div[role="radiogroup"] input[type="radio"] { display: none !important; }
    div[role="radiogroup"] label > div:first-child { display: none !important; }

    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        border: 2px solid #ea5656 !important;
        border-radius: 50% !important;
        width: 22px !important;
        height: 32px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-size: 16px !important;
        font-weight: bold !important;
        color: #ea5656 !important;
        background-color: white !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: background-color 0.1s;
    }

    div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {
        background-color: black !important;
        border-color: black !important;
        color: black !important;
    }

    div[role="radiogroup"] {
        display: flex;
        justify-content: space-between;
        padding: 5px 5px !important;
    }
    div[role="radiogroup"] label {
        flex: 1;
        display: flex;
        justify-content: center;
        margin: 0 !important;
    }

    /* 2. 표 디자인 (세로선, 레이아웃) */
    div[data-testid="stForm"] {
        border: 2px solid #333;
        padding: 0 !important;
        background: linear-gradient(
            to right, 
            #f0f2f6 0%, 
            #f0f2f6 15%, 
            #333 15%, 
            #333 calc(15% + 2px), 
            #ffffff calc(15% + 2px), 
            #ffffff 100%
        ) !important;
    }
    div[data-testid="stForm"] [data-testid="stVerticalBlock"] { gap: 0 !important; }
    div[data-testid="stForm"] [data-testid="stHorizontalBlock"] { gap: 0 !important; align-items: stretch !important; }

    .q-num-box {
        font-weight: 800;
        text-align: center;
        font-size: 16px;
        color: #333;
        width: 100%;
        padding-top: 9px;
    }
    .header-box {
        font-weight: bold;
        text-align: center;
        padding: 10px 0;
        font-size: 16px;
        color: #333;
    }
    .separator-line {
        border-top: 1px dashed #bbb;
        margin: 0;
        width: 100%;
        height: 1px;
    }
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    
    /* 시작 화면 전용 스타일 */
    .start-title {
        text-align: center;
        margin-bottom: 30px;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
if 'exam_started' not in st.session_state:
    st.session_state['exam_started'] = False
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {}
if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False

# ==============================================================================
# [화면 1] 시험 설정 및 응시자 정보 입력 화면
# ==============================================================================
if not st.session_state['exam_started']:
    st.markdown("<h1 class='start-title'>📝 OMR Answer Sheet</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.subheader("시험 선택")
        
        # 1. 시험 종류 선택
        exam_type = st.selectbox("시험 종류", logic.get_exam_types())
        
        # 2. 과목 선택 (시험 종류에 따라 변동)
        subjects = logic.get_subjects(exam_type)
        subject = st.selectbox("과목", subjects) if subjects else st.selectbox("과목", ["-"])
        
        # 3. 년도/회차 선택 (과목에 따라 변동)
        years = logic.get_years(exam_type, subject)
        year = st.selectbox("년도 및 회차", years) if years else st.selectbox("년도 및 회차", ["-"])
        
        st.divider()
        st.subheader("응시자 정보")
        
        # 4. 응시번호 및 성명 입력
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            user_number = st.text_input("응시번호 (숫자)", placeholder="12345")
        with col_inp2:
            user_name = st.text_input("성명", placeholder="홍길동")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 5. 시작 버튼
        start_btn = st.button("시험 시작 ▶", type="primary", use_container_width=True)
        
        if start_btn:
            if not user_name:
                st.warning("성명을 입력해주세요.")
            elif not year or year == "-":
                st.warning("시험 정보를 올바르게 선택해주세요.")
            else:
                # 정보 저장 및 화면 전환
                st.session_state['info_type'] = exam_type
                st.session_state['info_subject'] = subject
                st.session_state['info_year'] = year
                st.session_state['info_number'] = user_number
                st.session_state['info_name'] = user_name
                st.session_state['exam_started'] = True
                st.session_state['user_answers'] = {}
                st.session_state['submitted'] = False
                st.rerun()

# ==============================================================================
# [화면 2] OMR 답안 작성 화면
# ==============================================================================
else:
    # 저장된 정보 불러오기
    e_type = st.session_state['info_type']
    e_subj = st.session_state['info_subject']
    e_year = st.session_state['info_year']
    u_name = st.session_state['info_name']
    
    st.markdown(f"#### 📄 {e_type} > {e_subj}")
    st.caption(f"**{e_year}** | 응시자: **{u_name}**")

    # 정답 데이터 가져오기
    correct_answers = logic.get_answer_key(e_type, e_subj, e_year)
    total_q = len(correct_answers)

    if total_q > 0:
        with st.form("omr_form", border=False):
            
            # 헤더
            h1, h2 = st.columns([15, 85])
            with h1:
                st.markdown("<div class='header-box'>문번</div>", unsafe_allow_html=True)
            with h2:
                st.markdown("<div class='header-box'>답 란</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='border-top: 2px solid #333; width:100%; line-height:0;'>&nbsp;</div>", unsafe_allow_html=True)

            # 문항 반복
            for q in range(1, total_q + 1):
                if q != 1 and (q - 1) % 5 == 0:
                    st.markdown("<div class='separator-line'></div>", unsafe_allow_html=True)
                
                # 5단위 블록 상단 여백
                if (q - 1) % 5 == 0:
                    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

                r1, r2 = st.columns([15, 85])
                
                with r1:
                    st.markdown(f"<div class='q-num-box'>{q}</div>", unsafe_allow_html=True)
                
                with r2:
                    val = st.radio(
                        f"q_{q}", 
                        options=[1, 2, 3, 4, 5], 
                        horizontal=True, 
                        label_visibility="collapsed", 
                        index=None, 
                        key=f"q_{q}"
                    )
                    st.session_state['user_answers'][q] = val

            st.markdown("<div style='border-top: 2px solid #333; width:100%; line-height:0;'>&nbsp;</div>", unsafe_allow_html=True)
            st.markdown("<div style='background:white; padding:10px;'>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("채점하기", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submit_btn:
                st.session_state['submitted'] = True
                st.rerun()
    
    # 결과 화면
    if st.session_state['submitted']:
        st.divider()
        st.subheader(f"📊 {u_name}님의 결과")
        score, wrong_details = logic.grade_exam(st.session_state['user_answers'], correct_answers)
        
        st.info(f"점수: **{score:.1f}점**")
        
        if not wrong_details:
            st.success("완벽합니다! 만점입니다! 🎉")
        else:
            st.write(f"총 {len(wrong_details)}문항 오답:")
            for item in wrong_details:
                st.markdown(f"""
                <div style="background-color:#fff5f5; padding:8px; border-radius:5px; margin-bottom:5px; border:1px solid #ffcccc;">
                    <b>{item['q_num']}번</b> : 내 답 <b style="color:red;">{item['user_ans']}</b> 
                    / 정답 <b style="color:blue;">{item['correct_ans']}</b>
                </div>
                """, unsafe_allow_html=True)

        col_re1, col_re2 = st.columns(2)
        with col_re1:
            # 같은 시험 다시 풀기
            if st.button("이 시험 다시 풀기", use_container_width=True):
                st.session_state['user_answers'] = {}
                st.session_state['submitted'] = False
                for key in list(st.session_state.keys()):
                    if key.startswith("q_"):
                        del st.session_state[key]
                st.rerun()
        with col_re2:
            # 처음 화면으로 돌아가기
            if st.button("다른 시험 선택 (홈)", use_container_width=True):
                st.session_state['exam_started'] = False
                st.session_state['submitted'] = False
                st.session_state['user_answers'] = {}
                st.rerun()