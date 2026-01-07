import streamlit as st
import fitz  # PyMuPDF
import os
from PIL import Image
import io
import gc
import json

# [1] 데이터 로드 함수
@st.cache_data
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def get_available_exams():
    base_path = "output/leet"
    if not os.path.exists(base_path): return {}
    
    exams = {
        "추리논증": {},
        "언어이해": {}
    }
    
    subjects = {"c": "추리논증", "i": "언어이해"}
    
    for sub_code, sub_name in subjects.items():
        sub_path = os.path.join(base_path, sub_code)
        if os.path.exists(sub_path):
            folders = [f for f in os.listdir(sub_path) if os.path.isdir(os.path.join(sub_path, f))]
            sorted_folders = sorted(folders, key=lambda x: int(x) if x.isdigit() else (0 if "예비" in x else -1), reverse=True)

            for year in sorted_folders:
                exams[sub_name][year] = f"leet/{sub_code}/{year}"
    
    return exams

# [2] 폰트 경로 설정
def get_fonts():
    final_font_path = "MALGUN.TTF" if os.path.exists("MALGUN.TTF") else "malgun.ttf" if os.path.exists("malgun.ttf") else None
    title_font_path = "SBM.TTF" if os.path.exists("SBM.TTF") else "SBM.ttf" if os.path.exists("SBM.ttf") else None
    return final_font_path, title_font_path

# [3] 정답지 PDF 생성
def create_answer_pdf(selections, title):
    answer_db = load_answers()
    final_font_path, title_font_path = get_fonts()
    
    doc = fitz.open()
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

    def insert_plain_textbox(page, rect, text, fontsize, fontname, align=1):
        page.insert_textbox(rect, text, fontsize=fontsize, fontname=fontname, align=align)

    if not selections: 
        page = doc.new_page(width=PW, height=PH)
        return doc.tobytes()
    
    valid_keys = [k for k in selections.keys() if selections[k][2] == "logic"]
    
    if not valid_keys:
        page = doc.new_page(width=PW, height=PH)
        if final_font_path: page.insert_font(fontname=font_name, fontfile=final_font_path)
        else: page.insert_font(fontname="helv", fontfile=None)
        
        msg = "선택하신 문항(언어이해 등)은 정답표가 별도로 제공되지 않습니다."
        if final_font_path:
            page.insert_textbox(fitz.Rect(0, PH/2-20, PW, PH/2+20), msg, fontsize=12, fontname=font_name, align=1)
        else:
            page.insert_textbox(fitz.Rect(0, PH/2-20, PW, PH/2+20), "No Answer Key available.", fontsize=12, align=1)
        return doc.tobytes()

    sorted_q_nums = sorted(valid_keys); max_q_num = sorted_q_nums[-1] 
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
                insert_plain_textbox(page, get_v_center_rect(q_rect, header_fs, 2), "문항\n번호", header_fs, font_name, align=1)
                
                a_rect = fitz.Rect(col_start_x + q_col_w, header_y, col_start_x + col_pair_width, header_y + ROW_H)
                page.draw_rect(a_rect, color=(0,0,0), width=0.5)
                insert_plain_textbox(page, get_v_center_rect(a_rect, header_fs, 1), "정답", header_fs, font_name, align=1)

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
            y_k, val, type_code = selections[q_n]
            if type_code == "logic":
                row_data = answer_db.get(y_k)
                if not row_data:
                    row_data = answer_db.get(f"{y_k} (추리)", {}) 
                raw = row_data.get(str(val), {}).get("ans", "?")
                page.insert_textbox(get_v_center_rect(q_rect, 11), str(q_n), fontsize=11, fontname=font_name, align=1)
                page.insert_textbox(get_v_center_rect(a_rect, 11), circied_map.get(raw, raw), fontsize=11, fontname=font_name, align=1)
            elif type_code == "lang":
                page.insert_textbox(get_v_center_rect(q_rect, 11), str(q_n), fontsize=11, fontname=font_name, align=1)
                page.insert_textbox(get_v_center_rect(a_rect, 11), "-", fontsize=11, fontname=font_name, align=1)

    return doc.tobytes()

# [4] 문제지 PDF 생성
def create_problem_pdf(user_selections, title, show_source, one_q_per_row, available_exams, progress_bar=None):
    final_font_path, title_font_path = get_fonts()
    
    doc = fitz.open()
    PT = 2.83465
    PW = 297.0 * PT
    PH = 420.0 * PT
    
    # 여백 설정 (사용자 요청: 위-13, 아래-8, 좌-10, 우-10)
    base_m = 20 * PT
    M_TOP = base_m - (15 * PT)
    M_BOT = base_m - (10 * PT)
    M_LEFT = base_m - (6 * PT)
    M_RIGHT = base_m - (6 * PT)

    HEADER_H = 18 * PT
    FOOTER_H = 15 * PT
    COL_GAP = 10 * PT
    
    COL_W = (PW - M_LEFT - M_RIGHT - COL_GAP) / 2
    
    START_Y_NORMAL = M_TOP + HEADER_H + 7
    START_Y_CONT = M_TOP + HEADER_H + 55 
    
    font_alias = "my_font"; title_alias = "my_title"
    
    def draw_header(page, pg_num, title_text):
        pg_y = M_TOP + 10
        if final_font_path: page.insert_text((M_LEFT, pg_y), str(pg_num), fontname=font_alias, fontfile=final_font_path, fontsize=24, color=(0,0,0))
        else: page.insert_text((M_LEFT, pg_y), str(pg_num), fontsize=24, color=(0,0,0), fontname="helv")
        
        line_y = M_TOP + HEADER_H; title_y = line_y - 23
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
        bx = PW - M_RIGHT - tw; by = line_y - 7
        if final_font_path:
            page.insert_text((bx, by), btxt, fontname=font_alias, fontfile=final_font_path, fontsize=11, color=(0.4,0.4,0.4))
        else: page.insert_text((bx, by), btxt, fontsize=11, color=(0.4,0.4,0.4))
        
        page.draw_line((M_LEFT, line_y), (PW - M_RIGHT, line_y), color=(0.8,0.8,0.8), width=1.5)

    pg_cnt = 0
    curr_page = None
    slot_idx = 0 
    q_progress_idx = 0
    valid_count = len(user_selections)
    
    global_q_idx = 1

    for i in sorted(user_selections.keys()):
        y_display, val, type_code = user_selections[i]
        
        category = "언어이해" if type_code == "lang" else "추리논증"
        folder_path = available_exams.get(category, {}).get(y_display)
        if not folder_path: continue

        # [A] 언어이해
        if type_code == "lang":
            set_id = val 
            col_images = {1: [], 2: [], 3: []}
            
            q_count_in_set = 0
            
            p1 = f"output/{folder_path}/{set_id}_1_1.png"
            if os.path.exists(p1): col_images[1].append(p1)
            
            for sub in range(1, 6): 
                p2 = f"output/{folder_path}/{set_id}_2_{sub}.png"
                if os.path.exists(p2): 
                    col_images[2].append(p2)
                    if sub > 1: q_count_in_set += 1
                
            for sub in range(1, 4):
                p3 = f"output/{folder_path}/{set_id}_3_{sub}.png"
                if os.path.exists(p3): 
                    col_images[3].append(p3)
                    q_count_in_set += 1

            range_text = f"[{global_q_idx}~{global_q_idx + q_count_in_set - 1} 다음 글을 읽고 물음에 답하시오.]"

            for c_idx in range(1, 4):
                imgs = col_images[c_idx]
                if not imgs: continue 

                is_left_col = False
                if one_q_per_row:
                    is_new_page = True
                    is_left_col = True
                    if slot_idx % 2 != 0: slot_idx += 1 
                else:
                    if slot_idx % 2 == 0:
                        is_new_page = True
                        is_left_col = True
                    else:
                        is_new_page = False
                        is_left_col = False
                
                if is_new_page:
                    pg_cnt += 1
                    curr_page = doc.new_page(width=PW, height=PH)
                    draw_header(curr_page, pg_cnt, title)
                    curr_page.draw_line((PW/2, START_Y_NORMAL), (PW/2, PH-M_BOT-20), color=(0.8,0.8,0.8), width=0.5)

                cx = M_LEFT if is_left_col else M_LEFT + COL_W + COL_GAP
                cy = START_Y_NORMAL
                
                hh = 0
                if show_source:
                    year_text = f"{y_display}학년도"
                    start_q = (set_id - 1) * 3 + 1
                    end_q = set_id * 3
                    t = f"{year_text} LEET 언어이해 홀수형 {start_q}~{end_q}번"
                    
                    if c_idx == 1:
                        if final_font_path: curr_page.insert_text((cx, cy+12), t, fontname=font_alias, fontfile=final_font_path, fontsize=9, color=(0.4,0.4,0.4))
                        else: curr_page.insert_text((cx, cy+12), t, fontsize=9, color=(0.4,0.4,0.4))
                        hh = 20 
                    else:
                        hh = 20 

                iy = cy + hh 
                
                for img_path in imgs:
                    with Image.open(img_path) as pim:
                        sw, sh = pim.size
                        ih = sh * (COL_W / sw) 
                        
                        r = fitz.Rect(cx, iy, cx+COL_W, iy+ih)
                        b = io.BytesIO()
                        rgb_im = pim.convert('RGB')
                        rgb_im.save(b, format='JPEG', quality=95) 
                        curr_page.insert_image(r, stream=b.getvalue())
                        b.close()
                        
                        if "_1_1.png" in img_path:
                            curr_page.draw_rect(fitz.Rect(cx, iy, cx+250, iy+20), color=(1,1,1), fill=(1,1,1))
                            ts = range_text
                            tx_pos = (cx, iy + 15)
                            if final_font_path:
                                # [수정] 범위라벨 얇게 (Bold 제거)
                                curr_page.insert_text(tx_pos, ts, fontname=font_alias, fontfile=final_font_path, fontsize=12, color=(0,0,0))
                            else:
                                curr_page.insert_text(tx_pos, ts, fontsize=12, color=(0,0,0))

                        elif "_2_1.png" in img_path:
                            pass 

                        else:
                            curr_page.draw_rect(fitz.Rect(cx, iy, cx+19, iy+20), color=(1,1,1), fill=(1,1,1))
                            ns = f"{global_q_idx}."
                            if final_font_path:
                                # [수정] 언어이해 문제번호 굵게 (Bold 유지)
                                curr_page.insert_text((cx, iy+15), ns, fontname=font_alias, fontfile=final_font_path, fontsize=13, color=(0,0,0))
                                curr_page.insert_text((cx+0.7, iy+15), ns, fontname=font_alias, fontfile=final_font_path, fontsize=13, color=(0,0,0))
                            else:
                                curr_page.insert_text((cx, iy+15), ns, fontsize=13, color=(0,0,0))
                            
                            global_q_idx += 1 
                        
                        iy += ih 
                
                slot_idx += 1

        # [B] 추리논증
        else:
            sn = val 
            images_to_process = []
            img_1 = f"output/{folder_path}/{sn:02d}.png"
            if os.path.exists(img_1):
                images_to_process.append(img_1)
                img_2_a = f"output/{folder_path}/{sn:02d}_2.png"
                img_2_b = f"output/{folder_path}/{sn:02d}_02.png"
                if os.path.exists(img_2_a): images_to_process.append(img_2_a)
                elif os.path.exists(img_2_b): images_to_process.append(img_2_b)
            
            for img_path in images_to_process:
                is_continuation = "_2.png" in img_path or "_02.png" in img_path
                
                with Image.open(img_path) as pim:
                    sw, sh = pim.size
                    ih = sh * (COL_W / sw)
                    hh = 20 if (show_source and not is_continuation) else 0
                    
                    is_left_col = False
                    if one_q_per_row:
                        is_new_page = True
                        is_left_col = True
                        if slot_idx % 2 != 0: slot_idx += 1 
                    else:
                        if slot_idx % 2 == 0:
                            is_new_page = True
                            is_left_col = True
                        else:
                            is_new_page = False
                            is_left_col = False
                    
                    if is_new_page:
                        pg_cnt += 1
                        curr_page = doc.new_page(width=PW, height=PH)
                        draw_header(curr_page, pg_cnt, title)
                        curr_page.draw_line((PW/2, START_Y_NORMAL), (PW/2, PH-M_BOT-20), color=(0.8,0.8,0.8), width=0.5)
                    
                    cy = START_Y_CONT if is_continuation else START_Y_NORMAL
                    cx = M_LEFT if is_left_col else M_LEFT + COL_W + COL_GAP
                    iy = cy
                    
                    if show_source and not is_continuation:
                        year_text = f"{y_display}학년도"
                        t = f"{year_text} LEET 추리논증 홀수형 {val}번"
                        if final_font_path: curr_page.insert_text((cx, cy+12), t, fontname=font_alias, fontfile=final_font_path, fontsize=9, color=(0.4,0.4,0.4))
                        else: curr_page.insert_text((cx, cy+12), t, fontsize=9, color=(0.4,0.4,0.4))
                        iy += hh 

                    r = fitz.Rect(cx, iy, cx+COL_W, iy+ih)
                    b = io.BytesIO()
                    rgb_im = pim.convert('RGB')
                    rgb_im.save(b, format='JPEG', quality=95) 
                    curr_page.insert_image(r, stream=b.getvalue())
                    b.close()
                    
                    if not is_continuation:
                        curr_page.draw_rect(fitz.Rect(cx, iy, cx+18, iy+20), color=(1,1,1), fill=(1,1,1))
                        ns = f"{global_q_idx}."
                        global_q_idx += 1
                        
                        if final_font_path:
                            # [수정] 추리논증 문제번호 굵게 (Bold 유지)
                            curr_page.insert_text((cx+4, iy+17), ns, fontname=font_alias, fontfile=final_font_path, fontsize=13, color=(0,0,0))
                            curr_page.insert_text((cx+4.7, iy+17), ns, fontname=font_alias, fontfile=final_font_path, fontsize=13, color=(0,0,0))
                        else:
                            curr_page.insert_text((cx, iy+14), ns, fontsize=13, color=(0,0,0))
                
                slot_idx += 1
        
        q_progress_idx += 1
        if progress_bar: progress_bar.progress(q_progress_idx / valid_count)
        gc.collect()
    
    tot = len(doc); bw, bh = 60, 24
    for i, p in enumerate(doc):
        pg = i+1; cx = PW/2; by = PH - FOOTER_H/2 + bh/2
        p.draw_rect(fitz.Rect(cx-bw/2, by-bh, cx+bw/2, by), color=(0.4,0.4,0.4), width=0.8)
        ft = f"{pg}  /  {tot}"; tr = fitz.Rect(cx-bw/2, by-bh+6, cx+bw/2, by)
        if final_font_path:
            p.insert_textbox(tr, ft, fontname=font_alias, fontfile=final_font_path, fontsize=10, align=1, color=(0.4,0.4,0.4))
            p.insert_textbox(fitz.Rect(tr.x0+0.5, tr.y0, tr.x1+0.5, tr.y1), ft, fontname=font_alias, fontfile=final_font_path, fontsize=10, align=1, color=(0.4,0.4,0.4))
        else: p.insert_textbox(tr, ft, fontsize=10, align=1, color=(0.4,0.4,0.4))

    if doc.page_count == 0:
        page = doc.new_page(width=PW, height=PH)
        page.insert_text((100, 100), "No images found.", fontsize=12, color=(0,0,0))

    return doc.tobytes()