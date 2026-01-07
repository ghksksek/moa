import fitz  # PyMuPDF
import os

# ==========================================
# ⚙️ [설정] 
# ==========================================
CONFIG = {
    "margin_left": 86, "margin_right": 86,
    "mid_x_left": 408, "mid_x_right": 433,
    "bottom_cut": 113, 
    "last_bottom_cut": 180,
    "q1_top": 371, "q2_top": 242,          
    "std_left_top": 152, "std_right_top": 152,   
    "start_q_num": 1,       
    "dpi": 200              
}

# ==========================================
# 🛡️ 안전 저장 함수
# ==========================================
def safe_save_image(page, rect, path):
    safe_rect = fitz.Rect(
        max(0, rect.x0), max(0, rect.y0),
        min(page.rect.width, rect.x1), min(page.rect.height, rect.y1)
    )
    if safe_rect.width < 1 or safe_rect.height < 1:
        return
    try:
        page.get_pixmap(clip=safe_rect, dpi=CONFIG["dpi"]).save(path)
    except Exception as e:
        print(f"   [Error] 저장 실패: {e}")

# ==========================================
# ✂️ 상단 여백 자동 제거
# ==========================================
def auto_trim_top(page, rect):
    blocks = page.get_text("blocks", clip=rect)
    if not blocks: return rect
    min_y = min(b[1] for b in blocks)
    new_top = max(rect.y0, min_y - 5)
    return fitz.Rect(rect.x0, new_top, rect.x1, rect.y1)

# ==========================================
# 🛠️ 텍스트(문제번호) Y좌표 찾기
# ==========================================
def find_y_by_text(page, rect, target_num):
    if rect.width <= 0 or rect.height <= 0: return None
    text_instances = page.get_text("words", clip=rect)
    text_instances.sort(key=lambda x: x[1]) 

    target_str = str(target_num)
    target_str_dot = f"{target_num}."

    for word in text_instances:
        text = word[4].strip()
        if text == target_str or text == target_str_dot:
            return word[1] - 5 
    return None

# ==========================================
# 🚀 PDF 처리 로직
# ==========================================
def process_pdf(file_path, output_base_folder):
    filename = os.path.basename(file_path)
    file_stem = os.path.splitext(filename)[0]
    save_folder = os.path.join(output_base_folder, f"{file_stem}_결과")
    if not os.path.exists(save_folder): os.makedirs(save_folder)

    print(f"▶ 처리 시작: {filename}")

    doc = fitz.open(file_path)
    total_cols = doc.page_count * 2
    current_q_target = CONFIG["start_q_num"]
    
    ml, mr = CONFIG["margin_left"], CONFIG["margin_right"]
    mxl, mxr = CONFIG["mid_x_left"], CONFIG["mid_x_right"]
    bc, lbc = CONFIG["bottom_cut"], CONFIG["last_bottom_cut"]

    current_set_num = 1
    phase = 0  
    next_col_split_mode = False 

    for col_idx in range(total_cols):
        page_idx = col_idx // 2
        is_left_col = (col_idx % 2 == 0)
        p_num = page_idx + 1
        
        pg = doc.load_page(page_idx)
        w, h = pg.rect.width, pg.rect.height

        if p_num == 1:
            cur_top = CONFIG["q1_top"] if is_left_col else CONFIG["q2_top"]
        else:
            cur_top = CONFIG["std_left_top"] if is_left_col else CONFIG["std_right_top"]

        is_very_last_col = (col_idx == total_cols - 1)
        cur_bot = lbc if is_very_last_col else bc
        actual_bot_y = h - cur_bot
        if cur_top >= actual_bot_y: actual_bot_y = h 

        # 기본 영역 (Base Rect)
        if is_left_col:
            rect_base = fitz.Rect(ml, cur_top, mxl, actual_bot_y)
        else:
            rect_base = fitz.Rect(mxr, cur_top, w - mr, actual_bot_y)

        # ==========================================================
        # [Phase 0] 지문 단 (Set_N_1_1.png)
        # ==========================================================
        if phase == 0:
            optimized_rect = auto_trim_top(pg, rect_base)
            # [변경] _1 -> _1_1 로 통일
            safe_save_image(pg, optimized_rect, f"{save_folder}/{current_set_num}_1_1.png")
            phase = 1 

        # ==========================================================
        # [Phase 1] 문제 단 (Set_N_2_x.png)
        # ==========================================================
        elif phase == 1:
            q1_y = find_y_by_text(pg, rect_base, current_q_target)
            q2_y = find_y_by_text(pg, rect_base, current_q_target + 1)
            q3_y = find_y_by_text(pg, rect_base, current_q_target + 2)

            # [Case A] 문제 3개 -> 세트 종료
            if q1_y and q2_y and q3_y:
                ys = sorted([cur_top, q1_y, q2_y, q3_y, actual_bot_y])
                
                r1 = auto_trim_top(pg, fitz.Rect(rect_base.x0, ys[0], rect_base.x1, ys[1]))
                safe_save_image(pg, r1, f"{save_folder}/{current_set_num}_2_1.png")
                
                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[1], rect_base.x1, ys[2]), f"{save_folder}/{current_set_num}_2_2.png")
                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[2], rect_base.x1, ys[3]), f"{save_folder}/{current_set_num}_2_3.png")
                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[3], rect_base.x1, ys[4]), f"{save_folder}/{current_set_num}_2_4.png")

                current_q_target += 3
                current_set_num += 1
                phase = 0 

            # [Case B] 문제 2개
            elif q1_y and q2_y:
                ys = sorted([cur_top, q1_y, q2_y, actual_bot_y])
                
                r1 = auto_trim_top(pg, fitz.Rect(rect_base.x0, ys[0], rect_base.x1, ys[1]))
                safe_save_image(pg, r1, f"{save_folder}/{current_set_num}_2_1.png")

                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[1], rect_base.x1, ys[2]), f"{save_folder}/{current_set_num}_2_2.png")
                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[2], rect_base.x1, ys[3]), f"{save_folder}/{current_set_num}_2_3.png")

                current_q_target += 2
                phase = 2 
                next_col_split_mode = False 

            # [Case C] 문제 1개
            elif q1_y:
                ys = sorted([cur_top, q1_y, actual_bot_y])
                
                r1 = auto_trim_top(pg, fitz.Rect(rect_base.x0, ys[0], rect_base.x1, ys[1]))
                safe_save_image(pg, r1, f"{save_folder}/{current_set_num}_2_1.png")

                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[1], rect_base.x1, ys[2]), f"{save_folder}/{current_set_num}_2_2.png")

                current_q_target += 1
                phase = 2 
                next_col_split_mode = True 

            # [예외] OCR 실패 시
            else:
                h3 = rect_base.height / 3
                ys = [cur_top, cur_top+h3, cur_top+h3*2, actual_bot_y]
                r1 = auto_trim_top(pg, fitz.Rect(rect_base.x0, ys[0], rect_base.x1, ys[1]))
                safe_save_image(pg, r1, f"{save_folder}/{current_set_num}_2_1.png")
                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[1], rect_base.x1, ys[2]), f"{save_folder}/{current_set_num}_2_2.png")
                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[2], rect_base.x1, ys[3]), f"{save_folder}/{current_set_num}_2_3.png")
                
                current_q_target += 2
                phase = 2
                next_col_split_mode = False

        # ==========================================================
        # [Phase 2] 마지막 단 (Set_N_3_x.png)
        # ==========================================================
        elif phase == 2:
            if next_col_split_mode:
                # 쪼개지는 경우 (_3_1, _3_2)
                split_y = find_y_by_text(pg, rect_base, current_q_target + 1)
                if split_y is None: split_y = cur_top + (rect_base.height * 0.5)
                
                ys = sorted([cur_top, split_y, actual_bot_y])
                
                r1 = auto_trim_top(pg, fitz.Rect(rect_base.x0, ys[0], rect_base.x1, ys[1]))
                safe_save_image(pg, r1, f"{save_folder}/{current_set_num}_3_1.png")
                
                safe_save_image(pg, fitz.Rect(rect_base.x0, ys[1], rect_base.x1, ys[2]), f"{save_folder}/{current_set_num}_3_2.png")
                current_q_target += 2
            else:
                # 통으로 된 경우도 [변경] _3 -> _3_1 로 통일
                optimized_rect = auto_trim_top(pg, rect_base)
                safe_save_image(pg, optimized_rect, f"{save_folder}/{current_set_num}_3_1.png")
                current_q_target += 1

            current_set_num += 1
            phase = 0

    doc.close()
    print(f"✅ 완료: {filename} (마지막 세트번호: {current_set_num-1})\n")

def main():
    source_dir = "pdf_source"
    output_dir = "output"

    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"⚠️ '{source_dir}' 폴더가 생성되었습니다. PDF를 넣고 실행하세요.")
        return

    pdf_files = [f for f in os.listdir(source_dir) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"⚠️ PDF 파일 없음")
        return

    print(f"📂 발견: {len(pdf_files)}개")
    print("="*40)

    for pdf in pdf_files:
        try:
            process_pdf(os.path.join(source_dir, pdf), output_dir)
        except Exception as e:
            print(f"❌ 오류 ({pdf}): {e}")

    print("="*40)
    print("🎉 종료")

if __name__ == "__main__":
    main()