import streamlit as st
import streamlit.components.v1 as components
import fitz  # PyMuPDF
import os
from PIL import Image
import io
import gc
import base64
import json

# [0] 테마 및 설정
config_dir = ".streamlit"
config_file = os.path.join(config_dir, "config.toml")

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

theme_config = """
[theme]
primaryColor="#0614c1"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f0f2f6"
textColor="#262730"
font="sans serif"
"""

with open(config_file, "w", encoding='utf-8') as f:
    f.write(theme_config.strip())

st.set_page_config(layout="wide", page_title="기출 연습서 생성기", initial_sidebar_state="collapsed")

# ==============================================================================
# [CSS 스타일링] - 마지막 문항 세로선 처리를 위한 클래스 추가
# ==============================================================================
st.markdown("""
<style>
    /* 1. 기본 UI 초기화 */
    header, footer { display: none !important; }
    
    .block-container {
        max-width: 700px !important;
        width: 100% !important;
        padding: 2rem 10px 5rem 10px !important;
        margin: 0 auto !important;
    }

    /* 2. 입력창 강제 축소 및 정렬 */
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
    
    /* 3. 좌측 라벨 디자인 */
    
    /* (A) 일반 문항: 다음 문항과 선을 잇기 위해 높이를 길게(62px) 설정 */
    .q-label-container {
        display: flex;
        align-items: flex-start; 
        justify-content: flex-start;
        min-height: 62px; /* 여기가 핵심: 아래 여백까지 선을 그림 */
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

    /* (B) ★마지막 문항 전용★: 선을 잇지 않고 자기 높이(42px)에서 끝냄 */
    .q-label-container-last {
        display: flex;
        align-items: flex-start; 
        justify-content: flex-start;
        min-height: 42px !important; /* 높이를 딱 입력창만큼만! */
        height: 42px !important;     /* 더 이상 내려가지 않음 */
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

    /* 4. 버튼 스타일 */
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

    /* 레이아웃 여백 제거 */
    div[data-testid="column"] { 
        padding: 0 !important; 
        min-width: 0 !important; 
        flex: 1 1 0% !important; 
    }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }
    [data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }
    
    /* 모바일 미세 조정 */
    @media (max-width: 600px) {
        .q-label-container, .q-label-container-last { padding-right: 5px; margin-right: 3px; }
        .stSelectbox div[data-baseweb="select"] span { font-size: 12px !important; }
        div[data-baseweb="select"] svg { width: 10px !important; min-width: 10px !important; }
        button[kind="secondary"], .add-btn button, button[kind="primary"] { height: 45px !important; min-height: 45px !important; }
    }
</style>
""", unsafe_allow_html=True)

# [1] 데이터 로드
@st.cache_data
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

answer_db = load_answers()

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

def get_available_exams():
    base_path = "output/leet"
    if not os.path.exists(base_path): return {}
    exams = {}
    subjects = {"c": "추리", "i": "언어"}
    for sub_code, sub_name in subjects.items():
        sub_path = os.path.join(base_path, sub_code)
        if os.path.exists(sub_path):
            for year in [f for f in os.listdir(sub_path) if os.path.isdir(os.path.join(sub_path, f))]:
                exams[f"{year} ({sub_name})"] = f"leet/{sub_code}/{year}"
    return dict(sorted(exams.items(), reverse=True))

available_exams = get_available_exams()

# [3] UI 구성
final_font_path = "MALGUN.TTF" if os.path.exists("MALGUN.TTF") else "malgun.ttf" if os.path.exists("malgun.ttf") else None
title_font_path = "SBM.TTF" if os.path.exists("SBM.TTF") else "SBM.ttf" if os.path.exists("SBM.ttf") else None

c1, c2 = st.columns([1, 1])
with c1: 
    input_val = st.text_input("custom_title_input", placeholder="오답노트 이름", label_visibility="collapsed")
    custom_title = input_val if input_val else "나만의 기출 모음집"

c3, c4, c_blank = st.columns([2, 2, 3])
with c3: show_source = st.toggle("출처 표시", value=True)
with c4: one_q_per_row = st.toggle("1쪽 1문항", value=False)

st.divider()

# =========================================================
# 문항 생성 루프
# =========================================================
user_selections = {}
if available_exams:
    years_list = ["년도"] + list(available_exams.keys())
    
    for i in range(1, st.session_state.target_q_count + 1):
        
        row_cols = st.columns([1, 9], gap="small")
        
        # [핵심 로직] 마지막 문항인지 확인
        # 마지막 문항이면 'q-label-container-last' (높이 짧음, 선 끊김)
        # 아니면 'q-label-container' (높이 김, 선 연결됨)
        is_last_item = (i == st.session_state.target_q_count)
        label_class = "q-label-container-last" if is_last_item else "q-label-container"
        
        # 1. 좌측 라벨
        with row_cols[0]:
            st.markdown(f"""
            <div class="{label_class}">
                <span class="q-bullet">●</span> {i}문
            </div>
            """, unsafe_allow_html=True)
        
        # 2. 우측 입력영역
        with row_cols[1]:
            input_cols = st.columns([1, 1], gap="small")
            
            with input_cols[0]:
                y = st.selectbox(
                    "y", years_list, 
                    key=f"y_{i}", 
                    label_visibility="collapsed", 
                    on_change=on_year_change, args=(i,)
                )
            
            with input_cols[1]:
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
        
        # 여백 (마지막 문항이 아니면 선을 연결하기 위해 공간이 있어도 됨. 
        # 하지만 CSS에서 라벨 높이(62px)로 이미 처리했으므로 div height는 최소화하거나 없애도 됩니다.)
        # 단, 입력창 사이의 물리적 간격을 위해 유지하되, 
        # 마지막 문항의 라벨(42px)은 이 여백을 침범하지 않아 선이 끊깁니다.
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # =========================================================
    # 하단 버튼 영역
    # =========================================================
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    
    btn_row_cols = st.columns([1, 9], gap="small")
    
    with btn_row_cols[0]:
        st.empty() 
        
    with btn_row_cols[1]:
        btn_input_cols = st.columns([1, 1], gap="small")
        
        with btn_input_cols[0]:
            st.markdown('<div class="add-btn">', unsafe_allow_html=True)
            if st.button("＋", key="add_btn", use_container_width=True):
                increase_q()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn_input_cols[1]:
            if st.session_state.target_q_count > 1:
                if st.button("－", key="del_btn", type="secondary", use_container_width=True):
                    decrease_q()
                    st.rerun()
            else:
                st.button("－", disabled=True, use_container_width=True)

# [4] PDF 생성 로직 (이전과 동일)
def create_answer_pdf(selections, title):
    doc = fitz.open()
    SHOW_EXPLANATION = False 
    PT = 2.83465; PW = 210.0 * PT; PH = 297.0 * PT; MARGIN = 20 * PT
    font_name = "my_font"; title_font_name = "title_font"
    if not title_font_path: title_font_name = font_name 

    circied_map = {
        '1': '①', '2': '②', '3': '③', '4': '④', '5': '⑤',
        '6': '⑥', '7': '⑦', '8': '⑧', '9': '⑨', '10': '⑩', '?': '?' 
    }
    TABLE_START_Y = 140; ROW_H = 16 * PT; q_col_w = (PW - 2*MARGIN)/4 * 0.4; col_pair_width = (PW - 2*MARGIN)/4

    def get_v_center_rect(rect, font_size, lines=1):
        text_h = font_size * 1.3 * lines 
        pad_y = (rect.height - text_h) / 2
        return fitz.Rect(rect.x0, rect.y0 + max(0, pad_y), rect.x1, rect.y1)

    def insert_bold_textbox(page, rect, text, fontsize, fontname, align=1):
        page.insert_textbox(rect, text, fontsize=fontsize, fontname=fontname, align=align)
        bold_rect = fitz.Rect(rect.x0 + 0.3, rect.y0, rect.x1 + 0.3, rect.y1)
        page.insert_textbox(bold_rect, text, fontsize=fontsize, fontname=fontname, align=align)

    if not selections: return doc.write()
    sorted_q_nums = sorted(selections.keys()); max_q_num = sorted_q_nums[-1] 
    total_slots = ((max_q_num - 1) // 40 + 1) * 40
    
    for q_n in range(1, total_slots + 1):
        if (q_n - 1) % 40 == 0:
            page = doc.new_page(width=PW, height=PH)
            if final_font_path: page.insert_font(fontname=font_name, fontfile=final_font_path)
            if title_font_path: page.insert_font(fontname=title_font_name, fontfile=title_font_path)
            elif final_font_path: page.insert_font(fontname=title_font_name, fontfile=final_font_path)

            page.insert_textbox(fitz.Rect(0, 55, PW, 75), "신성우의 로직트리 제공", fontsize=10, fontname=font_name, color=(0.5,0.5,0.5), align=1)
            page.insert_textbox(fitz.Rect(0, 80, PW, 120), f"{title} - 정답표", fontsize=20, fontname=title_font_name, color=(0,0,0), align=1)

            header_y = TABLE_START_Y; header_fs = 11
            for i in range(4):
                col_start_x = MARGIN + (i * col_pair_width)
                q_rect = fitz.Rect(col_start_x, header_y, col_start_x + q_col_w, header_y + ROW_H)
                page.draw_rect(q_rect, color=(0,0,0), width=0.5)
                insert_bold_textbox(page, get_v_center_rect(q_rect, header_fs, 2), "문항\n번호", header_fs, font_name, align=1)
                
                a_rect = fitz.Rect(col_start_x + q_col_w, header_y, col_start_x + col_pair_width, header_y + ROW_H)
                page.draw_rect(a_rect, color=(0,0,0), width=0.5)
                insert_bold_textbox(page, get_v_center_rect(a_rect, header_fs, 1), "정답", header_fs, font_name, align=1)

            h_btm = TABLE_START_Y + ROW_H
            page.draw_line((MARGIN, h_btm), (PW - MARGIN, h_btm), color=(0,0,0), width=0.5)
            page.draw_line((MARGIN, h_btm + 2), (PW - MARGIN, h_btm + 2), color=(0,0,0), width=0.5)
            page.draw_rect(fitz.Rect(MARGIN, TABLE_START_Y, PW - MARGIN, TABLE_START_Y + ROW_H * 11), color=(0,0,0), width=2.0)

        local_idx = (q_n - 1) % 40; col_idx = local_idx // 10; row_idx = local_idx % 10 
        base_x = MARGIN + (col_idx * col_pair_width); base_y = TABLE_START_Y + ROW_H + (row_idx * ROW_H)
        q_rect = fitz.Rect(base_x, base_y, base_x + q_col_w, base_y + ROW_H)
        a_rect = fitz.Rect(base_x + q_col_w, base_y, base_x + col_pair_width, base_y + ROW_H)
        page.draw_rect(q_rect, color=(0,0,0), width=0.5); page.draw_rect(a_rect, color=(0,0,0), width=0.5)

        if q_n in selections:
            y_k, _ = selections[q_n]
            raw = answer_db.get(y_k, {}).get(str(q_n), {}).get("ans", "?")
            page.insert_textbox(get_v_center_rect(q_rect, 11), str(q_n), fontsize=11, fontname=font_name, align=1)
            page.insert_textbox(get_v_center_rect(a_rect, 11), circied_map.get(raw, raw), fontsize=11, fontname=font_name, align=1)

    return doc.write()

# [5] 메인 실행 버튼
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
valid_count = len(user_selections)
if st.button(f"🚀 {valid_count}문제 PDF 생성 (문제+정답)", type="primary", use_container_width=True):
    if valid_count == 0: st.warning("문제를 선택해주세요.")
    else:
        # A. 문제지 PDF 생성
        prog = st.progress(0); doc = fitz.open()
        PT = 2.83465; PW = 297.0 * PT; PH = 420.0 * PT; MARGIN = 20 * PT; HEADER_H = 18 * PT; FOOTER_H = 25 * PT
        COL_GAP = 12 * PT; COL_W = (PW - 2*MARGIN - COL_GAP)/2; START_Y = MARGIN + HEADER_H + 10
        font_alias = "my_font"; title_alias = "my_title"
        
        def draw_header(page, pg_num, title_text):
            pg_y = MARGIN + 10
            if final_font_path: page.insert_text((MARGIN, pg_y), str(pg_num), fontname=font_alias, fontfile=final_font_path, fontsize=24, color=(0,0,0))
            else: page.insert_text((MARGIN, pg_y), str(pg_num), fontsize=24, color=(0,0,0), fontname="helv")
            
            line_y = MARGIN + HEADER_H; title_y = line_y - 23
            use_font = title_font_path if title_font_path else final_font_path
            use_alias = title_alias if title_font_path else font_alias
            if use_font:
                tw = fitz.Font(fontfile=use_font).text_length(title_text, fontsize=27)
                tx = (PW - tw) / 2
                page.insert_text((tx, title_y), title_text, fontname=use_alias, fontfile=use_font, fontsize=27, color=(0,0,0))
                page.insert_text((tx+0.7, title_y), title_text, fontname=use_alias, fontfile=use_font, fontsize=27, color=(0,0,0))
            else:
                tw = fitz.Font("helv").text_length(title_text, fontsize=27)
                page.insert_text(((PW-tw)/2, title_y), title_text, fontsize=27, color=(0,0,0))
            
            btxt = "신성우의 로직트리 제공"
            if final_font_path: calc_font = fitz.Font(fontfile=final_font_path)
            else: calc_font = fitz.Font("helv")
            tw = calc_font.text_length(btxt, fontsize=11)
            bx = PW - MARGIN - tw; by = line_y - 7
            if final_font_path:
                page.insert_text((bx, by), btxt, fontname=font_alias, fontfile=final_font_path, fontsize=11, color=(0.4,0.4,0.4))
                page.insert_text((bx+0.3, by), btxt, fontname=font_alias, fontfile=final_font_path, fontsize=11, color=(0.4,0.4,0.4))
            else: page.insert_text((bx, by), btxt, fontsize=11, color=(0.4,0.4,0.4))
            page.draw_line((MARGIN, line_y), (PW - MARGIN, line_y), color=(0.8,0.8,0.8), width=1.5)

        pg_cnt = 1; curr_page = doc.new_page(width=PW, height=PH)
        draw_header(curr_page, pg_cnt, custom_title)
        curr_page.draw_line((PW/2, START_Y), (PW/2, PH-FOOTER_H), color=(0.8,0.8,0.8), width=0.5)
        yl, yr = START_Y, START_Y; p_idx = 0

        for i in sorted(user_selections.keys()):
            y_display, sn = user_selections[i]
            folder_path = available_exams[y_display]
            ip = f"output/{folder_path}/{sn:02d}.jpg"
            if os.path.exists(ip):
                with Image.open(ip) as pim:
                    sw, sh = pim.size; ih = sh * (COL_W / sw); hh = 20 if show_source else 0; th = hh + ih
                    col = None
                    if one_q_per_row:
                         if yl + th <= PH-FOOTER_H-5: col='l'
                    else:
                        if yl <= yr and yl + th <= PH-FOOTER_H-5: col='l'
                        elif yr + th <= PH-FOOTER_H-5: col='r'
                    
                    if col is None:
                        pg_cnt += 1; curr_page = doc.new_page(width=PW, height=PH)
                        draw_header(curr_page, pg_cnt, custom_title)
                        curr_page.draw_line((PW/2, START_Y), (PW/2, PH-FOOTER_H), color=(0.8,0.8,0.8), width=0.5)
                        yl, yr = START_Y, START_Y; col = 'l'

                    if col == 'l': cx=MARGIN; cy=yl; yl+=th+20
                    else: cx=MARGIN+COL_W+COL_GAP; cy=yr; yr+=th+20
                    
                    iy = cy
                    if show_source:
                        t = f"{y_display} LEET {sn}번"
                        if final_font_path: curr_page.insert_text((cx, cy+12), t, fontname=font_alias, fontfile=final_font_path, fontsize=9, color=(0.4,0.4,0.4))
                        else: curr_page.insert_text((cx, cy+12), t, fontsize=9, color=(0.4,0.4,0.4))
                        iy += hh
                    
                    r = fitz.Rect(cx, iy, cx+COL_W, iy+ih)
                    b = io.BytesIO(); pim.save(b, format='JPEG', quality=90)
                    curr_page.insert_image(r, stream=b.getvalue()); b.close()
                    curr_page.draw_rect(fitz.Rect(cx, iy, cx+19, iy+20), color=(1,1,1), fill=(1,1,1))
                    ns = f"{i}."
                    if final_font_path:
                        curr_page.insert_text((cx, iy+14), ns, fontname=font_alias, fontfile=final_font_path, fontsize=13, color=(0,0,0))
                        curr_page.insert_text((cx+0.7, iy+14), ns, fontname=font_alias, fontfile=final_font_path, fontsize=13, color=(0,0,0))
                    else: curr_page.insert_text((cx, iy+14), ns, fontsize=13, color=(0,0,0))
            p_idx += 1; prog.progress(p_idx / valid_count); gc.collect()
        
        tot = len(doc); bw, bh = 60, 24
        for i, p in enumerate(doc):
            pg = i+1; cx = PW/2; by = PH - FOOTER_H/2 + bh/2
            p.draw_rect(fitz.Rect(cx-bw/2, by-bh, cx+bw/2, by), color=(0.4,0.4,0.4), width=0.8)
            ft = f"{pg}  /  {tot}"; tr = fitz.Rect(cx-bw/2, by-bh+6, cx+bw/2, by)
            if final_font_path:
                p.insert_textbox(tr, ft, fontname=font_alias, fontfile=final_font_path, fontsize=10, align=1, color=(0.4,0.4,0.4))
                p.insert_textbox(fitz.Rect(tr.x0+0.5, tr.y0, tr.x1+0.5, tr.y1), ft, fontname=font_alias, fontfile=final_font_path, fontsize=10, align=1, color=(0.4,0.4,0.4))
            else: p.insert_textbox(tr, ft, fontsize=10, align=1, color=(0.4,0.4,0.4))

        prob_pdf = doc.write(); doc.close()
        ans_pdf = create_answer_pdf(user_selections, custom_title)
        safe_name = custom_title.strip()
        b64_prob = base64.b64encode(prob_pdf).decode(); b64_ans = base64.b64encode(ans_pdf).decode()
        
        js = f"""<script>
            function save(filename, data) {{
                const link = document.createElement('a'); link.href = 'data:application/pdf;base64,' + data; link.download = filename;
                document.body.appendChild(link); link.click(); document.body.removeChild(link);
            }}
            setTimeout(function() {{ save('{safe_name}_문제.pdf', '{b64_prob}'); }}, 500);
            setTimeout(function() {{ save('{safe_name}_해설.pdf', '{b64_ans}'); }}, 1500);
        </script>"""
        components.html(js, height=0)
        c_d1, c_d2 = st.columns(2)
        c_d1.download_button("📥 문제지 받기", prob_pdf, f"{safe_name}_문제.pdf", "application/pdf", use_container_width=True)
        c_d2.download_button("📥 정답지 받기", ans_pdf, f"{safe_name}_정답.pdf", "application/pdf", use_container_width=True)
        st.success("생성 완료!")