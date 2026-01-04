import os
import fitz  # PyMuPDF
from PIL import Image
import io
import re

# ==========================================
# [설정] 경로 설정
SOURCE_FOLDER = "pdf_source"  # PDF 파일 넣어둘 폴더
OUTPUT_ROOT = "output"        # 결과물 저장될 폴더

# [설정] 이미지 품질
# PNG는 무손실 압축이므로 IMG_QUALITY(압축률) 설정은 사용하지 않습니다.
ZOOM_FACTOR = 2.0     # 해상도 배율 (2.0 = 200dpi 수준, 높을수록 선명하지만 용량 커짐)

# ==========================================
# [중요] LEET 프리셋 값 (app.py 기준)
# ==========================================
MARGIN_LEFT = 86       # 왼쪽 여백
MARGIN_RIGHT = 86      # 오른쪽 여백

MID_X_LEFT = 408       # 왼쪽 단 끝 x좌표
MID_X_RIGHT = 433      # 오른쪽 단 시작 x좌표

BOTTOM_CUT = 113       # 기본 하단 여백 (왼쪽 단 전체 + 1~39페이지 오른쪽 단)
LAST_BOTTOM_CUT = 180  # [수정됨] 마지막 페이지 '오른쪽 단' 전용 하단 여백

# 1페이지 상단 여백
Q1_TOP = 371           # 1페이지 왼쪽 시작
Q2_TOP = 242           # 1페이지 오른쪽 시작

# 나머지 페이지 상단 여백
STD_LEFT_TOP = 152     # 일반 왼쪽 시작
STD_RIGHT_TOP = 152    # 일반 오른쪽 시작
# ==========================================

def parse_filename(filename):
    """ 파일명에서 폴더명 생성 """
    match = re.match(r"(\d{4})([A-Za-z]+)(.+)(홀수형|짝수형)", filename)
    if match:
        return f"{match.group(1)}_{match.group(2)}_{match.group(3)}_{match.group(4)}"
    return os.path.splitext(filename)[0]

def process_pdfs():
    # 1. 폴더 확인
    if not os.path.exists(SOURCE_FOLDER):
        print(f"❌ '{SOURCE_FOLDER}' 폴더가 없습니다. 폴더를 만들고 PDF를 넣어주세요.")
        return

    pdf_files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ '{SOURCE_FOLDER}' 폴더 안에 PDF 파일이 없습니다.")
        return

    print(f"🚀 총 {len(pdf_files)}개의 파일을 변환합니다.\n")

    # 2. 파일 반복 처리
    for pdf_file in pdf_files:
        folder_name = parse_filename(pdf_file)
        save_path = os.path.join(OUTPUT_ROOT, folder_name)
        
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        full_path = os.path.join(SOURCE_FOLDER, pdf_file)
        doc = fitz.open(full_path)
        
        print(f"🔄 처리 중: {pdf_file}")
        
        q_cnt = 1
        last_page_idx = len(doc) - 1
        
        # 3. 페이지 반복 처리
        for i, page in enumerate(doc):
            w = page.rect.width
            h = page.rect.height
            
            # (1) 상단 여백 결정
            if i == 0:
                c_tl = Q1_TOP      # 1페이지 왼쪽
                c_tr = Q2_TOP      # 1페이지 오른쪽
            else:
                c_tl = STD_LEFT_TOP
                c_tr = STD_RIGHT_TOP
                
            # (2) 하단 여백 결정
            # 왼쪽 단: 항상 기본 여백(113) 사용
            bottom_l = BOTTOM_CUT
            
            # 오른쪽 단: 마지막 페이지일 때만 180, 나머지는 113
            if i == last_page_idx:
                bottom_r = LAST_BOTTOM_CUT
            else:
                bottom_r = BOTTOM_CUT

            # (3) 자르기 영역 계산 (x0, y0, x1, y1)
            # 왼쪽 단
            rect_l = fitz.Rect(MARGIN_LEFT, c_tl, MID_X_LEFT, h - bottom_l)
            # 오른쪽 단
            rect_r = fitz.Rect(MID_X_RIGHT, c_tr, w - MARGIN_RIGHT, h - bottom_r)

            # (4) 이미지 저장
            mat = fitz.Matrix(ZOOM_FACTOR, ZOOM_FACTOR)
            crops = [rect_l, rect_r]
            
            for rect in crops:
                if rect.width > 0 and rect.height > 0:
                    pix = page.get_pixmap(matrix=mat, clip=rect)
                    
                    # 너무 작은 조각(오류)이 아니면 저장
                    if pix.width > 10 and pix.height > 10:
                        img_data = pix.tobytes("ppm")
                        img = Image.open(io.BytesIO(img_data))
                        
                        # [변경점] 확장자 png로 변경
                        out_filename = f"{q_cnt:02d}.png"
                        out_path = os.path.join(save_path, out_filename)
                        
                        # [변경점] PNG 포맷 저장 (PNG는 무손실이므로 quality 옵션 제외)
                        img.save(out_path, "PNG", optimize=True)
                        q_cnt += 1

        print(f"   ✅ 완료! (총 {q_cnt-1}문제 추출됨)")
        doc.close()

    print("\n🎉 모든 변환 작업이 끝났습니다!")

if __name__ == "__main__":
    process_pdfs()