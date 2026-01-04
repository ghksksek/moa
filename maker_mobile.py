import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import logic

# [0] 테마 및 설정
config_dir = ".streamlit"
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

with open(os.path.join(config_dir, "config.toml"), "w", encoding='utf-8') as f:
    f.write("""[theme]
primaryColor="#0614c1"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f0f2f6"
textColor="#262730"
font="sans serif"
""")

st.set_page_config(layout="wide", page_title="모바일 기출 생성기", initial_sidebar_state="collapsed")

# [1] CSS 스타일 (모바일 전용 디자인)
st.markdown("""
<style>
    /* 1. 기본 UI 초기화 */
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    .block-container { 
        padding-top: 1.5rem !important; 
        padding-bottom: 5rem; 
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* 2. 문항 헤더 (심플 텍스트 스타일) */
    .slot-header { 
        background-color: transparent !important; 
        color: #000000 !important;                
        font-weight: 600; 
        font-size: 18px;                          
        border-radius: 0px !important;        
        height: auto !important; 
        line-height: 1.5; 
        text-align: left !important; 
        width: 100%;
        display: flex;           
        align-items: center;     
        margin-bottom: 25px !important; 
        padding-left: 2px;       
    }
    
    .q-bullet {
        color: #000000 !important; 
        margin-right: 8px;         
        font-size: 14px;           
        line-height: 1;
    }
    
    /* 3. 입력창 중앙 정렬 강화 */
    .stSelectbox label { display: none !important; }
    
    div[data-baseweb="select"] > div {
        background-color: #f8f9fa !important;
        border-color: #e0e0e0 !important;
        border-radius: 8px !important;
        min-height: 45px !important; 
        height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
    }
    
    div[data-baseweb="select"] > div > div:first-child {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 0 auto !important;
        padding: 0 !important;
        position: absolute !important;
        left: 0 !important;
        right: 0 !important;
    }

    div[data-baseweb="select"] span {
        font-size: 14px !important;
        color: #333;
        text-align: center !important;
        width: 100% !important;
        display: block !important;
    }
    
    div[data-baseweb="select"] svg {
        position: absolute !important;
        right: 10px !important;
        z-index: 10 !important;
        margin: 0 !important;
    }

    /* 4. 오답노트 이름 입력창 */
    .stTextInput input {
        text-align: center;
        min-height: 45px;
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 600;
    }

    /* 5. 토글 스위치 */
    div[data-testid="stColumn"] label[data-baseweb="checkbox"] {
        white-space: nowrap !important;
    }
    div[data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }

    /* 6. 버튼 스타일 (기존 Streamlit 버튼) */
    button[kind="secondary"] {
        height: 55px !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 20px !important;
        width: 100% !important;
        border: 2px solid #e0e0e0 !important;
    }
    button[data-testid="baseButton-secondary"]:has(div:contains("＋")) {
        color: #0614c1 !important;
        background-color: #f0f7ff !important;
        border-color: #0614c1 !important;
    }
    button[data-testid="baseButton-secondary"]:has(div:contains("－")) {
        color: #ff4b4b !important;
        background-color: #fff5f5 !important;
        border-color: #ff4b4b !important;
    }
    button[kind="primary"] {
        background-color: #0614c1 !important; 
        border-color: #0614c1 !important;
        height: 55px !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        margin-top: 15px !important;
    }
    
    /* 7. [NEW] HTML 다운로드 링크 버튼 스타일 */
    /* 기존 버튼과 똑같이 생겼지만, 실제로는 <a> 태그입니다 */
    .dwn-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 55px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 16px;
        text-decoration: none !important;
        margin-top: 0px;
        box-sizing: border-box;
        cursor: pointer;
        line-height: 1.2;
        text-align: center;
    }
    .dwn-btn:hover {
        text-decoration: none !important;
        opacity: 0.9;
    }
    /* 흰색 배경 버튼 (기존 secondary 스타일) */
    .dwn-white {
        background-color: #ffffff;
        color: #333333 !important;
        border: 2px solid #e0e0e0;
    }
    /* 텍스트 색상 강제 지정 */
    .dwn-white:visited, .dwn-white:active, .dwn-white:link {
        color: #333333 !important;
    }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    .element-container { margin-bottom: 5px !important; }
</style>
""", unsafe_allow_html=True)

# [2] 세션 관리
if 'target_q_count' not in st.session_state: st.session_state.target_q_count = 5 
def increase_q(): st.session_state.target_q_count += 1
def decrease_q():
    if st.session_state.target_q_count > 1: st.session_state.target_q_count -= 1

def on_subject_change(idx):
    if f"subj_{idx}" in st.session_state:
        new_subj = st.session_state[f"subj_{idx}"]
        if new_subj != "과목":
            for k in range(idx + 1, st.session_state.target_q_count + 1):
                st.session_state[f"subj_{k}"] = new_subj

def on_year_change(idx):
    if f"y_{idx}" in st.session_state:
        ny = st.session_state[f"y_{idx}"]
        if ny != "년도":
            for k in range(idx + 1, st.session_state.target_q_count + 1): st.session_state[f"y_{k}"] = ny

# [3] 데이터 로드 (logic.py)
available_exams = logic.get_available_exams()
subject_list = ["과목", "추리논증"]

# [4] UI 구성
raw_title = st.text_input("custom_title_input", placeholder="오답노트 이름", label_visibility="collapsed")
custom_title = raw_title if raw_title else "나만의 기출 모음집"

c_t1, c_t2 = st.columns([1, 1])
with c_t1: show_source = st.toggle("출처 표시", value=True)
with c_t2: one_q_per_row = st.toggle("1쪽 1문항", value=False)

st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

# 문항 생성 루프
user_selections = {}
if available_exams:
    years_list = ["년도"] + list(available_exams.keys())
    
    for i in range(1, st.session_state.target_q_count + 1):
        st.markdown(f"""
        <div class='slot-header'>
            <span class='q-bullet'>●</span> {i} 문
        </div>
        """, unsafe_allow_html=True)
        
        # 3단 컬럼 구성
        col_subj, col_y, col_n = st.columns([1.2, 1, 1], gap="small")
        
        with col_subj:
            subj = st.selectbox("subject", subject_list, key=f"subj_{i}", label_visibility="collapsed", on_change=on_subject_change, args=(i,))
        with col_y:
            y = st.selectbox("y", years_list, key=f"y_{i}", label_visibility="collapsed", on_change=on_year_change, args=(i,))
        with col_n:
            if subj != "과목" and y != "년도":
                mv = 35 if y.split()[0] in ['2017','2018'] else 40
                n_str = st.selectbox("n", ["문항 번호"] + [f"{k}번" for k in range(1, mv+1)], key=f"n_{i}", label_visibility="collapsed")
                if n_str != "문항 번호":
                    user_selections[i] = (y, int(n_str.replace("번", "")))
            else:
                st.selectbox("n", ["문항 번호"], key=f"n_{i}", disabled=True, label_visibility="collapsed")
        
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # 버튼 영역
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    b_col1, b_col2 = st.columns(2, gap="small")
    with b_col1:
        if st.button("＋", key="add_btn", use_container_width=True): increase_q(); st.rerun()
    with b_col2:
        if st.session_state.target_q_count > 1:
            if st.button("－", key="del_btn", type="secondary", use_container_width=True): decrease_q(); st.rerun()
        else:
            st.button("－", disabled=True, use_container_width=True)

# [5] 메인 실행 및 다운로드 로직 (HTML 링크 방식 적용)
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
valid_count = len(user_selections)

# 1. 생성 버튼 클릭 시 로직
if st.button(f"🚀 {valid_count}문제 PDF 생성 (문제+해설)", type="primary", use_container_width=True):
    if valid_count == 0:
        st.warning("문제를 선택해주세요.")
    else:
        prog = st.progress(0)
        
        st.session_state['prob_pdf'] = logic.create_problem_pdf(user_selections, custom_title, show_source, one_q_per_row, available_exams, prog)
        st.session_state['ans_pdf'] = logic.create_answer_pdf(user_selections, custom_title)
        st.session_state['safe_name'] = custom_title.strip()
        st.session_state['generated'] = True
        
        st.success("생성 완료! 아래 버튼을 눌러 다운로드하세요.")

# 2. 파일이 생성되어 있다면 HTML 다운로드 링크 표시
if st.session_state.get('generated', False):
    prob_pdf = st.session_state['prob_pdf']
    ans_pdf = st.session_state['ans_pdf']
    safe_name = st.session_state['safe_name']
    
    # PDF 데이터를 Base64 문자열로 변환
    b64_prob = base64.b64encode(prob_pdf).decode()
    b64_ans = base64.b64encode(ans_pdf).decode()
    
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    
    c_d1, c_d2 = st.columns(2, gap="small")
    
    # [핵심] st.download_button 대신 HTML <a> 태그를 버튼처럼 보이게 렌더링
    with c_d1:
        href_prob = f'<a href="data:application/pdf;base64,{b64_prob}" download="{safe_name}_문제.pdf" class="dwn-btn dwn-white">📥 문제지 받기</a>'
        st.markdown(href_prob, unsafe_allow_html=True)
        
    with c_d2:
        href_ans = f'<a href="data:application/pdf;base64,{b64_ans}" download="{safe_name}_해설.pdf" class="dwn-btn dwn-white">📥 정답지 받기</a>'
        st.markdown(href_ans, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)