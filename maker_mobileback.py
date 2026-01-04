import streamlit as st
import streamlit.components.v1 as components
import base64
import os  # <--- [중요] 이 줄이 빠져서 에러가 났습니다. 다시 추가했습니다!
import logic  # logic.py를 불러옵니다

# [0] 테마 및 설정
config_dir = ".streamlit"
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

config_path = os.path.join(config_dir, "config.toml")
with open(config_path, "w", encoding='utf-8') as f:
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
    
    /* 2. 문항 헤더 (검정 알약 스타일) */
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
    
    /* 3. 입력창 디자인 */
    .stSelectbox label { display: none !important; }
    div[data-baseweb="select"] > div {
        background-color: #f8f9fa !important;
        border-color: #e0e0e0 !important;
        border-radius: 8px !important;
        min-height: 45px !important; 
        height: 45px !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    div[data-baseweb="select"] span {
        font-size: 14px !important;
        color: #333;
        text-align: center;
        width: 100%;
        display: block;
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

    /* 6. 버튼 스타일 */
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
    button[kind="primary"]:hover {
        background-color: #040e94 !important;
        border-color: #040e94 !important;
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

def on_year_change(idx):
    if f"y_{idx}" in st.session_state:
        ny = st.session_state[f"y_{idx}"]
        if ny != "년도":
            for k in range(idx + 1, st.session_state.target_q_count + 1): st.session_state[f"y_{k}"] = ny

# [3] 데이터 로드 (logic.py에서 가져옴)
available_exams = logic.get_available_exams()

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
        
        col_y, col_n = st.columns([1, 1], gap="small")
        
        with col_y:
            y = st.selectbox(
                "y", years_list, 
                key=f"y_{i}", 
                label_visibility="collapsed", 
                on_change=on_year_change, args=(i,)
            )
            
        with col_n:
            if y != "년도":
                mv = 35 if y.split()[0] in ['2017','2018'] else 40
                n_str = st.selectbox(
                    "n", ["문항 번호"] + [f"{k}번" for k in range(1, mv+1)], 
                    key=f"n_{i}", 
                    label_visibility="collapsed"
                )
                if n_str != "문항 번호":
                    user_selections[i] = (y, int(n_str.replace("번", "")))
            else:
                st.selectbox("n", ["문항 번호"], key=f"n_{i}", disabled=True, label_visibility="collapsed")
        
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # 하단 조작 버튼
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    b_col1, b_col2 = st.columns(2, gap="small")
    
    with b_col1:
        if st.button("＋", key="add_btn", use_container_width=True):
            increase_q()
            st.rerun()
            
    with b_col2:
        if st.session_state.target_q_count > 1:
            if st.button("－", key="del_btn", type="secondary", use_container_width=True):
                decrease_q()
                st.rerun()
        else:
            st.button("－", disabled=True, use_container_width=True)

# [5] 메인 실행 (PDF 생성 - logic.py 사용)
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
valid_count = len(user_selections)

# 1. 생성 버튼 클릭 시 로직
if st.button(f"🚀 {valid_count}문제 PDF 생성 (문제+해설)", type="primary", use_container_width=True):
    if valid_count == 0:
        st.warning("문제를 선택해주세요.")
    else:
        # logic.py 호출
        prog = st.progress(0)
        
        # 생성 후 세션 상태에 저장
        st.session_state['prob_pdf'] = logic.create_problem_pdf(user_selections, custom_title, show_source, one_q_per_row, available_exams, prog)
        st.session_state['ans_pdf'] = logic.create_answer_pdf(user_selections, custom_title)
        st.session_state['safe_name'] = custom_title.strip()
        st.session_state['generated'] = True
        
        st.success("생성 완료! 아래 버튼을 눌러 다운로드하세요.")

# 2. 파일이 생성되어 있다면 다운로드 버튼 표시
if st.session_state.get('generated', False):
    prob_pdf = st.session_state['prob_pdf']
    ans_pdf = st.session_state['ans_pdf']
    safe_name = st.session_state['safe_name']
    
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    
    c_d1, c_d2 = st.columns(2)
    c_d1.download_button("📥 문제지 받기", prob_pdf, f"{safe_name}_문제.pdf", "application/pdf", use_container_width=True)
    c_d2.download_button("📥 정답지 받기", ans_pdf, f"{safe_name}_해설.pdf", "application/pdf", use_container_width=True)
    
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)