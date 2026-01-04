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
    exams = {}
    subjects = {"c": "추리", "i": "언어"}
    
    for sub_code, sub_name in subjects.items():
        sub_path = os.path.join(base_path, sub_code)
        if os.path.exists(sub_path):
            # 폴더 목록 읽기
            folders = [f for f in os.listdir(sub_path) if os.path.isdir(os.path.join(sub_path, f))]
            
            for year in folders:
                # [확장성] 추리만 꼬리표 떼기
                if sub_name == "추리":
                    key_name = year
                else:
                    key_name = f"{year} ({sub_name})"
                exams[key_name] = f"leet/{sub_code}/{year}"
    
    # [정렬 로직 수정] 예비 -> 2009 -> ... -> 2026 순서 (예비를 맨 뒤로, 혹은 맨 앞으로? 보통 년도 역순이므로 예비는 가장 옛날)
    def sort_key(item):
        k = item[0]
        if "예비" in k:
            return -1  # 숫자로 변환 안 되므로 -1 (가장 과거 취급)
        try:
            return int(k.split()[0])
        except:
            return 0 # 알 수 없는 문자는 0

    # 내림차순 정렬 (2026 -> ... -> 2009 -> 예비)
    return dict(sorted(exams.items(), key=sort_key, reverse=True))

# [2] 폰트 경로 설정
def get_fonts():
    final_font_path = "MALGUN.TTF" if os.path.exists("MALGUN.TTF") else "malgun.ttf" if os.path.exists("malgun.ttf") else None
    title_font_path = "SBM.TTF" if os.path.exists("SBM.TTF") else "SBM.ttf" if os.path.exists("SBM.ttf") else None
    return final_font_path, title_font_path

# [3] 정답지 PDF 생성 로직
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
            
            # [정답 찾기] 순수 키 -> 실패시 (추리) 부착
            row_data = answer_db.get(y_k)
            if not row_data:
                row_data = answer_db.get(f"{y_k} (추리)", {})
            
            raw = row_data.get(str(q_n), {}).get("ans", "?")
            
            page.insert_textbox(get_v_center_rect(q_rect, 11), str(q_n), fontsize=11, fontname=font_name, align=1)
            page.insert_textbox(get_v_center_rect(a_rect, 11), circied_map.get(raw, raw), fontsize=11, fontname=font_name, align=1)

    return doc.write()

# ... (앞부분 import 및 get_available_exams, create_answer_pdf 등은 그대로 유지) ...

# [4] 문제지 PDF 생성 로직 (이어지는 문제 높이 개별 설정)
def create_problem_pdf(user_selections, title, show_source, one_q_per_row, available_exams, progress_bar=None):
    final_font_path, title_font_path = get_fonts()
    
    doc = fitz.open()
    PT = 2.83465; PW = 297.0 * PT; PH = 420.0 * PT; MARGIN = 20 * PT; HEADER_H = 18 * PT; FOOTER_H = 25 * PT
    COL_GAP = 12 * PT; COL_W = (PW - 2*MARGIN - COL_GAP)/2
    
    # ====================================================================
    # [설정] 시작 높이 조절 (여기서 숫자를 바꾸세요)
    # ====================================================================
    # 1. 일반 문제 시작 높이 (기존과 동일)
    START_Y_NORMAL = MARGIN + HEADER_H + 7
    
    # 2. 이어지는 문제(_2) 시작 높이 (텍스트가 없으니 조금 더 위로 올려도 됨)
    # 예: 일반 문제보다 20포인트 더 위로 올리고 싶으면 값을 줄이세요.
    START_Y_CONT = MARGIN + HEADER_H + 55
    # ====================================================================
    
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

    pg_cnt = 0
    curr_page = None
    slot_idx = 0 
    q_progress_idx = 0
    valid_count = len(user_selections)

    for i in sorted(user_selections.keys()):
        y_display, sn = user_selections[i]
        
        folder_path = available_exams.get(y_display)
        if not folder_path:
            folder_path = available_exams.get(f"{y_display} (추리)", "")
        if not folder_path: continue

        images_to_process = []
        
        img_1 = f"output/{folder_path}/{sn:02d}.png"
        if os.path.exists(img_1):
            images_to_process.append(img_1)
            
            img_2_a = f"output/{folder_path}/{sn:02d}_2.png"
            img_2_b = f"output/{folder_path}/{sn:02d}_02.png"
            
            if os.path.exists(img_2_a):
                images_to_process.append(img_2_a)
            elif os.path.exists(img_2_b):
                images_to_process.append(img_2_b)
        
        for img_path in images_to_process:
            is_continuation = "_2.png" in img_path or "_02.png" in img_path
            
            with Image.open(img_path) as pim:
                sw, sh = pim.size
                ih = sh * (COL_W / sw)
                hh = 20 if (show_source and not is_continuation) else 0
                th = hh + ih
                
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
                    # 구분선은 일반 시작 높이 기준으로 그림 (일관성 유지)
                    curr_page.draw_line((PW/2, START_Y_NORMAL), (PW/2, PH-FOOTER_H), color=(0.8,0.8,0.8), width=0.5)
                
                # [핵심] 문제 종류에 따라 시작 높이(cy) 결정
                if is_continuation:
                    cy = START_Y_CONT
                else:
                    cy = START_Y_NORMAL
                
                cx = MARGIN if is_left_col else MARGIN + COL_W + COL_GAP
                
                iy = cy
                
                if show_source and not is_continuation:
                    t = f"{y_display} LEET {sn}번"
                    if final_font_path: curr_page.insert_text((cx, cy+12), t, fontname=font_alias, fontfile=final_font_path, fontsize=9, color=(0.4,0.4,0.4))
                    else: curr_page.insert_text((cx, cy+12), t, fontsize=9, color=(0.4,0.4,0.4))
                    
                iy += hh 
                
                r = fitz.Rect(cx, iy, cx+COL_W, iy+ih)
                
# [수정 전]
                # b = io.BytesIO()
                # pim.save(b, format='PNG') 
                # curr_page.insert_image(r, stream=b.getvalue())
                # b.close()

                # [수정 후] 용량 문제 해결 코드 (고화질 JPEG 압축)
                b = io.BytesIO()
                # PNG의 투명도 정보를 제거하고 RGB로 변환 (JPEG 저장을 위해 필수)
                rgb_im = pim.convert('RGB')
                # quality=95로 설정하면 화질 저하는 눈으로 구별 불가하지만 용량은 확 줄어듭니다.
                rgb_im.save(b, format='JPEG', quality=95) 
                curr_page.insert_image(r, stream=b.getvalue())
                b.close()
                
                if not is_continuation:
                    # 지우개
                    curr_page.draw_rect(fitz.Rect(cx, iy, cx+18, iy+20), color=(1,1,1), fill=(1,1,1))
                    
                    # 번호
                    ns = f"{i}."
                    if final_font_path:
                        curr_page.insert_text((cx, iy+14), ns, fontname=font_alias, fontfile=final_font_path, fontsize=13, color=(0,0,0))
                        curr_page.insert_text((cx+0.7, iy+14), ns, fontname=font_alias, fontfile=final_font_path, fontsize=13, color=(0,0,0))
                    else:
                        curr_page.insert_text((cx, iy+14), ns, fontsize=13, color=(0,0,0))
            
            slot_idx += 1
        
        q_progress_idx += 1
        if progress_bar:
            progress_bar.progress(q_progress_idx / valid_count)
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

    return doc.write()