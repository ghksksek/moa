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

st.set_page_config(layout="wide", page_title="모바일 기출 생성기", initial_sidebar_state="collapsed")

# ==============================================================================
# [CSS] 모바일 전용 스타일링
# ==============================================================================
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
    
    /* 2. 문항 헤더 (텍스트 형태, 여백 및 두께 조정) */
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
    
    /* 불릿 포인트 (ㅇ 모양) */
    .q-bullet {
        color: #000000 !important; 
        margin-right: 8px;         
        font-size: 14px;           
        line-height: 1;
    }
    
    /* 3. 입력창 디자인 (Selectbox) */
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
    
    /* 텍스트 중앙 정렬 */
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

    /* 6. 하단 조작 버튼 (+ / -) 스타일 */
    button[kind="secondary"] {
        height: 55px !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 20px !important;
        width: 100% !important;
        border: 2px solid #e0e0e0 !important;
    }
    
    /* + 버튼 */
    button[data-testid="baseButton-secondary"]:has(div:contains("＋")) {
        color: #0614c1 !important;
        background-color: #f0f7ff !important;
        border-color: #0614c1 !important;
    }

    /* - 버튼 */
    button[data-testid="baseButton-secondary"]:has(div:contains("－")) {
        color: #ff4b4b !important;
        background-color: #fff5f5 !important;
        border-color: #ff4b4b !important;
    }

    /* 7. PDF 생성 버튼 */
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

    /* 간격 미세 조정 */
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    .element-container { margin-bottom: 5px !important; }
</style>
""", unsafe_allow_html=True)

# [1] 정답 데이터 로드
@st.cache_data
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

answer_db = load_answers()

# [2] 세션 및 데이터
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

# 1. 오답노트 이름 입력 (수정된 부분: 변수에 바로 할당)
raw_title = st.text_input("custom_title_input", placeholder="오답노트 이름", label_visibility="collapsed")
# 값이 있으면 그걸 쓰고, 없으면 기본값 사용
custom_title = raw_title if raw_title else "나만의 기출 모음집"

# 2. 토글 버튼
c_t1, c_t2 = st.columns([1, 1])
with c_t1: show_source = st.toggle("출처 표시", value=True)
with c_t2: one_q_per_row = st.toggle("1쪽 1문항", value=False)

# 토글과 1문 사이 여백
st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

# =========================================================
# 문항 생성 루프
# =========================================================
user_selections = {}
if available_exams:
    years_list = ["년도"] + list(available_exams.keys())
    
    for i in range(1, st.session_state.target_q_count + 1):
        
        # 1. 헤더 (심플 텍스트)
        st.markdown(f"""
        <div class='slot-header'>
            <span class='q-bullet'>●</span> {i} 문
        </div>
        """, unsafe_allow_html=True)
        
        # 2. 년도 & 번호 선택
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
        
        # 간격
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # =========================================================
    # 하단 조작 버튼
    # =========================================================
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

# [4] PDF 생성 로직 (수정 완료: custom_title 변수 사용)
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
            
            # [확인] 여기에 custom_title 변수가 정상적으로 전달됩니다.
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

# [5] 메인 실행 버튼 (가장 하단)
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
valid_count = len(user_selections)
if st.button(f"🚀 {valid_count}문제 PDF 생성 (문제+해설)", type="primary", use_container_width=True):
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
        # [확인] 여기서도 custom_title이 정상적으로 전달됩니다.
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
        c_d2.download_button("📥 정답지 받기", ans_pdf, f"{safe_name}_해설.pdf", "application/pdf", use_container_width=True)
        st.success("생성 완료!")