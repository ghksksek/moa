import streamlit as st
import omrlogic

# --- 페이지 설정 ---
st.set_page_config(page_title="모바일 OMR", layout="centered")

# --- CSS 스타일 (반응형 끄기 및 디자인 고정) ---
st.markdown("""
<style>
    /* =================================================================
       1. [초강력 수정] 화면 폭 강제 고정 (PC/모바일 동일하게 보이기)
       ================================================================= */
    
    /* 앱 전체 너비를 스마트폰 사이즈(약 360px)로 강제 제한하고 중앙 정렬 */
    .block-container {
        max-width: 360px !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        margin: 0 auto !important;
    }

    /* =================================================================
       2. [초강력 수정] 컬럼 줄바꿈 방지 (모바일 두 줄 현상 해결)
       ================================================================= */
    
    /* Streamlit이 모바일에서 컬럼을 세로로 쌓는 것을 강제로 막음 */
    div[data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important; /* 무조건 가로 나열 */
        flex-wrap: nowrap !important;   /* 줄바꿈 절대 금지 */
    }

    /* =================================================================
       3. OMR 디자인 (표 그리기)
       ================================================================= */
    
    /* OMR 카드 컨테이너 (border=True로 만든 박스) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 2px solid #333 !important;
        border-radius: 0px !important;
        background: linear-gradient(
            to right, 
            #f0f2f6 0%, 
            #f0f2f6 50px,  /* 50px 지점까지 회색 (문번) */
            #333 50px, 
            #333 52px,     /* 2px 세로선 */
            #ffffff 52px, 
            #ffffff 100%
        ) !important;
        padding: 0 !important;
    }

    /* [왼쪽 칸: 문번] 너비 50px 고정 */
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"]:nth-of-type(1) {
        min-width: 50px !important;
        max-width: 50px !important;
        width: 50px !important;
        padding: 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* [오른쪽 칸: 답란] 나머지 영역 */
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"]:nth-of-type(2) {
        min-width: 0 !important; /* 내용이 넘쳐도 줄바꿈 안되게 */
        padding: 0 5px !important;
        display: flex;
        align-items: center;
    }

    /* =================================================================
       4. 라디오 버튼 (타원형) 커스텀
       ================================================================= */
    div[role="radiogroup"] input[type="radio"], 
    div[role="radiogroup"] label > div:first-child { display: none !important; }

    /* 알 디자인 */
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        border: 2px solid #ea5656 !important;
        border-radius: 50% !important;
        width: 24px !important;
        height: 30px !important;
        display: flex; justify-content: center; align-items: center;
        font-size: 14px !important; font-weight: bold !important;
        color: #ea5656 !important; background: white !important;
        margin: 0 !important;
    }

    /* 선택시 검정 */
    div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {
        background-color: black !important; border-color: black !important; color: white !important;
    }

    /* 알 배치 */
    div[role="radiogroup"] {
        display: flex; justify-content: space-between;
        width: 100% !important; padding: 4px 0 !important;
    }
    div[role="radiogroup"] label {
        flex: 1; display: flex; justify-content: center; margin: 0 !important; padding: 0 !important;
    }

    /* =================================================================
       5. 기타 요소
       ================================================================= */
    /* 폼 투명화 */
    div[data-testid="stForm"] { border: none !important; padding: 0 !important; }

    /* 텍스트 & 구분선 */
    .q-num-box { font-weight: 800; text-align: center; font-size: 14px; color: #333; padding-top: 10px; }
    .header-box { font-weight: bold; text-align: center; font-size: 14px; color: #333; padding: 10px 0; }
    .separator-line { position: absolute; left:0; right:0; border-top: 1px dashed #bbb; height: 1px; }

    /* 채점 버튼 */
    .stButton > button {
        margin-top: 15px; border: 2px solid #333; font-weight: bold; width: 100%;
    }
    .start-title { text-align: center; color: #333; margin-bottom: 20px;}

</style>
""", unsafe_allow_html=True)

# --- 세션 초기화 ---
if 'exam_started' not in st.session_state: st.session_state['exam_started'] = False
if 'user_answers' not in st.session_state: st.session_state['user_answers'] = {}
if 'submitted' not in st.session_state: st.session_state['submitted'] = False

# ==============================================================================
# [화면 1] 설정
# ==============================================================================
if not st.session_state['exam_started']:
    st.markdown("<h1 class='start-title'>📝 OMR Answer Sheet</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.subheader("시험 설정")
        exam_type = st.selectbox("시험 종류", omrlogic.get_exam_types())
        subjects = omrlogic.get_subjects(exam_type)
        subject = st.selectbox("과목", subjects) if subjects else st.selectbox("과목", ["-"])
        years = omrlogic.get_years(exam_type, subject)
        year = st.selectbox("년도", years) if years else st.selectbox("년도", ["-"])
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1: user_number = st.text_input("수험번호")
        with c2: user_name = st.text_input("성명")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("시험 시작", type="primary", use_container_width=True):
            if not user_name or not year or year == "-":
                st.warning("정보를 입력하세요.")
            else:
                st.session_state.update({
                    'info_type': exam_type, 'info_subject': subject, 'info_year': year,
                    'info_number': user_number, 'info_name': user_name,
                    'exam_started': True, 'user_answers': {}, 'submitted': False
                })
                st.rerun()

# ==============================================================================
# [화면 2] OMR 작성
# ==============================================================================
else:
    e_subj = st.session_state['info_subject']
    u_name = st.session_state['info_name']
    
    st.markdown(f"**{e_subj}** | {u_name}")

    correct_answers = omrlogic.get_answer_key(st.session_state['info_type'], e_subj, st.session_state['info_year'])
    total_q = len(correct_answers)

    if total_q > 0:
        with st.form("omr_form", border=False):
            # OMR 표 부분
            with st.container(border=True):
                # 헤더
                h1, h2 = st.columns([1, 6]) # 비율 설정 (CSS가 50px로 강제하므로 큰 의미는 없지만 구조 유지용)
                with h1: st.markdown("<div class='header-box'>문번</div>", unsafe_allow_html=True)
                with h2: st.markdown("<div class='header-box'>답 란</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='border-top: 2px solid #333; width:100%; line-height:0;'>&nbsp;</div>", unsafe_allow_html=True)

                for q in range(1, total_q + 1):
                    if q != 1 and (q - 1) % 5 == 0:
                        st.markdown("<div class='separator-line'></div>", unsafe_allow_html=True)
                    if (q - 1) % 5 == 0:
                        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

                    r1, r2 = st.columns([1, 6])
                    with r1:
                        st.markdown(f"<div class='q-num-box'>{q}</div>", unsafe_allow_html=True)
                    with r2:
                        # 라디오 버튼
                        val = st.radio(f"q_{q}", [1,2,3,4,5], horizontal=True, label_visibility="collapsed", key=f"q_{q}")
                        st.session_state['user_answers'][q] = val
            
            # 버튼은 표 바깥으로
            submit_btn = st.form_submit_button("채점하기", type="primary", use_container_width=True)
            
            if submit_btn:
                st.session_state['submitted'] = True
                st.rerun()
    
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
            if st.button("다시 풀기", use_container_width=True):
                st.session_state['user_answers'] = {}
                st.session_state['submitted'] = False
                st.rerun()
        with c2:
            if st.button("홈으로", use_container_width=True):
                st.session_state['exam_started'] = False
                st.rerun()