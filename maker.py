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

st.set_page_config(layout="wide", page_title="기출 연습서 생성기", initial_sidebar_state="collapsed")

# [1] CSS 스타일
st.markdown("""
<style>
    header, footer { display: none !important; }
    .block-container {
        max-width: 1000px !important;
        width: 100% !important;
        padding: 2rem 10px 5rem 10px !important;
        margin: 0 auto !important;
    }
    div[data-baseweb="select"], div[data-testid="stSelectbox"] {
        width: 100% !important;
        min-width: 0 !important;
        flex: 1 1 0% !important; 
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #f7f9fc !important;
        border-color: #e0e6ed !important;
        border-radius: 8px !important;
        min-height: 42px !important;
        height: 42px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        min-width: 0px !important; 
        padding: 0 2px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div > div:first-child {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 0px !important; 
        min-width: 0px !important;
        flex-grow: 1 !important; 
        flex-shrink: 1 !important;
        overflow: hidden !important; 
        margin: 0 auto !important;
        padding: 0 !important;
    }
    .stSelectbox div[data-baseweb="select"] span {
        font-size: 13px !important;
        color: #333 !important;
        text-align: center !important;
        display: block !important;
        width: 100% !important;
        min-width: 0px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    div[data-baseweb="select"] svg {
        width: 12px !important;
        min-width: 12px !important;
        flex-shrink: 0 !important;
        margin-left: 2px !important;
    }
    .stTextInput input {
        text-align: left !important;
        min-width: 0px !important;
        width: 100% !important;
        padding-left: 10px !important;
    }
    .stSelectbox label, .stTextInput label { display: none !important; }
    .q-label-container {
        display: flex;
        align-items: flex-start; 
        justify-content: flex-start;
        min-height: 62px; 
        height: 100%;
        padding-top: 12px; 
        font-size: 16px !important; 
        font-weight: 800;
        color: #333;
        border-right: 2px solid #e0e6ed; 
        padding-right: 8px;
        margin-right: 5px;
        white-space: nowrap; 
    }
    .q-label-container-last {
        display: flex;
        align-items: flex-start; 
        justify-content: flex-start;
        min-height: 42px !important; 
        height: 42px !important;      
        padding-top: 12px; 
        font-size: 16px !important; 
        font-weight: 800;
        color: #333;
        border-right: 2px solid #e0e6ed; 
        padding-right: 8px;
        margin-right: 5px;
        white-space: nowrap; 
    }
    .q-bullet {
        color: #000000 !important;
        margin-right: 4px;
        font-size: 10px;
        margin-top: 4px; 
    }
    button[kind="secondary"], .add-btn button, button[kind="primary"] {
        font-weight: 900;
        height: 50px !important; 
        min-height: 50px !important;
        border-radius: 12px !important;
        width: 100%;
        margin: 0 !important;
        box-sizing: border-box !important;
        padding: 0 !important;
    }
    button[kind="secondary"] {
        border: 1px solid #e0e0e0 !important;
        background-color: #ffffff !important;
        color: #777777 !important;
        font-size: 20px !important;
    }
    button[kind="secondary"]:hover {
        background-color: #f5f5f5 !important;
        color: #333 !important;
    }
    .add-btn button {
        border: 1px dashed #bbbbbb !important;
        background-color: #fafafa !important;
        color: #777777 !important;
        font-size: 20px !important;
    }
    .add-btn button:hover {
        background-color: #f0f0f0 !important;
        color: #333 !important;
    }
    button[kind="primary"] {
        background-color: #0614c1 !important;
        border-color: #0614c1 !important;
        font-size: 16px !important;
        margin-top: 20px !important;
    }
    button[kind="primary"]:hover {
        background-color: #040e94 !important;
        border-color: #040e94 !important;
    }
    div[data-testid="InputInstructions"] { display: none !important; }
    div[data-testid="column"] { 
        padding: 0 !important; 
        min-width: 0 !important; 
        flex: 1 1 0% !important; 
    }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }
    [data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }
    @media (max-width: 600px) {
        .q-label-container, .q-label-container-last { padding-right: 5px; margin-right: 3px; }
        .stSelectbox div[data-baseweb="select"] span { font-size: 12px !important; }
        div[data-baseweb="select"] svg { width: 10px !important; min-width: 10px !important; }
        button[kind="secondary"], .add-btn button, button[kind="primary"] { height: 45px !important; min-height: 45px !important; }
    }
</style>
""", unsafe_allow_html=True)

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

available_exams = logic.get_available_exams()
subject_list = ["과목", "추리논증", "언어이해"]

c1, c2 = st.columns([1, 1])
with c1:
    raw_title = st.text_input("custom_title_input", placeholder="오답노트 이름", label_visibility="collapsed")
    custom_title = raw_title if raw_title else "나만의 기출 모음집"

c3, c4, c_blank = st.columns([2, 2, 4])
with c3: show_source = st.toggle("출처 표시", value=True)
with c4: one_q_per_row = st.toggle("오른쪽 비우기", value=False)

st.divider()

user_selections = {}
if available_exams:
    for i in range(1, st.session_state.target_q_count + 1):
        
        row_cols = st.columns([1, 9], gap="small")
        is_last_item = (i == st.session_state.target_q_count)
        label_class = "q-label-container-last" if is_last_item else "q-label-container"
        
        with row_cols[0]:
            st.markdown(f"""
            <div class="{label_class}">
                <span class="q-bullet">●</span> {i}문
            </div>
            """, unsafe_allow_html=True)
        
        with row_cols[1]:
            input_cols = st.columns([1, 1, 1], gap="small")
            
            with input_cols[0]:
                subj = st.selectbox("subject", subject_list, key=f"subj_{i}", label_visibility="collapsed", on_change=on_subject_change, args=(i,))

            with input_cols[1]:
                current_years = ["년도"]
                if subj in available_exams:
                    current_years += list(available_exams[subj].keys())
                    
                y = st.selectbox("y", current_years, key=f"y_{i}", label_visibility="collapsed", on_change=on_year_change, args=(i,))
            
            with input_cols[2]:
                if subj != "과목" and y != "년도":
                    if subj == "언어이해":
                        ranges = [f"{k*3+1}~{k*3+3}" for k in range(10)]
                        n_str = st.selectbox("n", ["문항 선택"] + ranges, key=f"n_{i}", label_visibility="collapsed")
                        if n_str != "문항 선택":
                            first_num = int(n_str.split("~")[0])
                            set_id = (first_num - 1) // 3 + 1
                            user_selections[i] = (y, set_id, "lang")
                    else:
                        mv = 40
                        y_str = y.split()[0] 
                        if y_str.isdigit():
                            y_int = int(y_str)
                            if 2010 <= y_int <= 2018: mv = 35
                        
                        n_str = st.selectbox("n", ["문항 번호"] + [f"{k}번" for k in range(1, mv+1)], key=f"n_{i}", label_visibility="collapsed")
                        if n_str != "문항 번호":
                            user_selections[i] = (y, int(n_str.replace("번", "")), "logic")
                else:
                    st.selectbox("n", ["문항 번호"], key=f"n_{i}", disabled=True, label_visibility="collapsed")
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    btn_row_cols = st.columns([1, 9], gap="small")
    
    with btn_row_cols[0]: st.empty() 
    with btn_row_cols[1]:
        btn_input_cols = st.columns([1, 1], gap="small")
        with btn_input_cols[0]:
            st.markdown('<div class="add-btn">', unsafe_allow_html=True)
            if st.button("＋", key="add_btn", use_container_width=True):
                increase_q(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_input_cols[1]:
            if st.session_state.target_q_count > 1:
                if st.button("－", key="del_btn", type="secondary", use_container_width=True):
                    decrease_q(); st.rerun()
            else:
                st.button("－", disabled=True, use_container_width=True)

st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
valid_count = len(user_selections)

if st.button(f"🚀 {valid_count}문제 PDF 생성", type="primary", use_container_width=True):
    if valid_count == 0:
        st.warning("문제를 선택해주세요.")
    else:
        prog = st.progress(0)
        st.session_state['prob_pdf'] = logic.create_problem_pdf(user_selections, custom_title, show_source, one_q_per_row, available_exams, prog)
        st.session_state['ans_pdf'] = logic.create_answer_pdf(user_selections, custom_title)
        st.session_state['safe_name'] = custom_title.strip()
        st.session_state['generated'] = True 
        # [수정] 여기서 st.success 제거 (중복 방지)

if st.session_state.get('generated', False):
    prob_pdf = st.session_state['prob_pdf']
    ans_pdf = st.session_state['ans_pdf']
    safe_name = st.session_state['safe_name']
    
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    c_d1, c_d2 = st.columns(2)
    c_d1.download_button("📥 문제지 받기", prob_pdf, f"{safe_name}_문제.pdf", "application/pdf", use_container_width=True)
    c_d2.download_button("📥 정답지 받기", ans_pdf, f"{safe_name}_정답.pdf", "application/pdf", use_container_width=True)
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
    st.success("생성 완료!")