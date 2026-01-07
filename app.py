import streamlit as st
import fitz  # PyMuPDF
import os

st.set_page_config(layout="wide")
st.title("🏭 PSAT/LEET 마스터 (자르기 전용)")

# --- 0. 기본 설정 및 프리셋 ---
default_values = {
    "margin_left": 86, "margin_right": 86,
    "mid_x_left": 408, "mid_x_right": 433,
    "bottom_cut": 113, "last_bottom_cut": 180,
    "q1_top": 371, "q2_top": 242,
    "std_left_top": 152, "std_right_top": 152
}
for key, val in default_values.items():
    if key not in st.session_state: st.session_state[key] = val

def apply_leet_preset():
    st.session_state.margin_left = 86
    st.session_state.margin_right = 86
    st.session_state.mid_x_left = 408
    st.session_state.mid_x_right = 433
    st.session_state.bottom_cut = 113
    st.session_state.last_bottom_cut = 180
    st.session_state.q1_top = 371
    st.session_state.q2_top = 242
    st.session_state.std_left_top = 152
    st.session_state.std_right_top = 152

# ==========================================
# 메인 화면: 문제 자르기 (탭 제거됨)
# ==========================================

# 사이드바 (설정)
st.sidebar.markdown("### 1️⃣ 자르기 설정")
st.sidebar.button("🔄 LEET 맞춤값(180/113) 불러오기", on_click=apply_leet_preset)

save_format = st.sidebar.radio("💾 저장 형식", ("PDF 문서 (텍스트 선택 가능)", "PNG 이미지"), index=1) # 기본값을 PNG로 변경
start_save = st.sidebar.button("실행: 전체 문제 추출하기", type="primary")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 시험 정보")
exam_year = st.sidebar.number_input("연도", 2000, 2030, 2024)
exam_type = st.sidebar.selectbox("시험 종류", ["LEET", "PSAT", "MDEET"])
exam_subject = st.sidebar.text_input("과목명", "추리논증")
exam_book_type = st.sidebar.text_input("책형", "홀수형")

folder_name = f"output/{exam_year}_{exam_type}_{exam_subject}_{exam_book_type}"
master_pdf_name = f"{folder_name}/{exam_year}_{exam_type}_{exam_subject}_{exam_book_type}_통합본.pdf"

uploaded_file = st.file_uploader("원본 PDF 파일을 올려주세요", type="pdf")

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    last_page_idx = doc.page_count
    
    # 사이즈 정보 표시
    p1 = doc[0]
    w_mm = p1.rect.width * 0.352778
    h_mm = p1.rect.height * 0.352778
    st.info(f"📄 **원본 파일**: {doc.page_count}페이지 / 크기: **{w_mm:.1f} x {h_mm:.1f} mm**")

    # 좌표 설정 UI
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown("##### 👀 미리보기 설정")
        preview_page_num = st.number_input("페이지 이동", 1, doc.page_count, 1)
        zoom_level = st.slider("확대 배율", 1.0, 3.0, 1.0, 0.5)
    
    with col_view2:
        st.markdown("##### 📏 좌표 미세조정")
        c1, c2 = st.columns(2)
        with c1: st.session_state.margin_left = st.number_input("왼쪽 여백", key="ml", value=st.session_state.margin_left)
        with c2: st.session_state.margin_right = st.number_input("오른쪽 여백", key="mr", value=st.session_state.margin_right)
        c3, c4 = st.columns(2)
        with c3: st.session_state.mid_x_left = st.number_input("중앙선 왼쪽", key="mxl", value=st.session_state.mid_x_left)
        with c4: st.session_state.mid_x_right = st.number_input("중앙선 오른쪽", key="mxr", value=st.session_state.mid_x_right)
        st.session_state.bottom_cut = st.number_input("기본 하단 여백", key="bc", value=st.session_state.bottom_cut)
        
        if preview_page_num == 1:
            c5, c6 = st.columns(2)
            with c5: st.session_state.q1_top = st.number_input("1번(좌) 머리", key="q1", value=st.session_state.q1_top)
            with c6: st.session_state.q2_top = st.number_input("2번(우) 머리", key="q2", value=st.session_state.q2_top)
        else:
            c5, c6 = st.columns(2)
            with c5: st.session_state.std_left_top = st.number_input("홀수(좌) 머리", key="sl", value=st.session_state.std_left_top)
            with c6: st.session_state.std_right_top = st.number_input("짝수(우) 머리", key="sr", value=st.session_state.std_right_top)

        if preview_page_num == last_page_idx:
            st.session_state.last_bottom_cut = st.number_input("40번 하단 여백", key="lbc", value=st.session_state.last_bottom_cut)

    # 변수 할당
    margin_left = st.session_state.margin_left
    margin_right = st.session_state.margin_right
    mid_x_left = st.session_state.mid_x_left
    mid_x_right = st.session_state.mid_x_right
    bottom_cut = st.session_state.bottom_cut
    last_bottom_cut = st.session_state.last_bottom_cut
    q1_top, q2_top = st.session_state.q1_top, st.session_state.q2_top
    std_left_top, std_right_top = st.session_state.std_left_top, st.session_state.std_right_top

    # 미리보기 그리기
    st.divider()
    page_guide = doc.load_page(preview_page_num - 1)
    page_h, page_w = page_guide.rect.height, page_guide.rect.width
    shape = page_guide.new_shape()
    
    if preview_page_num == 1: tl, tr = q1_top, q2_top
    else: tl, tr = std_left_top, std_right_top
    cur_br = last_bottom_cut if preview_page_num == last_page_idx else bottom_cut

    shape.draw_line((margin_left, 0), (margin_left, page_h)); shape.finish(color=(0,0,1))
    shape.draw_line((mid_x_left, 0), (mid_x_left, page_h)); shape.finish(color=(0,0,1))
    shape.draw_line((mid_x_right, 0), (mid_x_right, page_h)); shape.finish(color=(0,0,1))
    shape.draw_line((page_w - margin_right, 0), (page_w - margin_right, page_h)); shape.finish(color=(0,0,1))
    shape.draw_line((0, tl), (mid_x_left, tl)); shape.finish(color=(1,0,0))
    shape.draw_line((mid_x_right, tr), (page_w, tr)); shape.finish(color=(1,0,0))
    shape.draw_line((0, page_h - bottom_cut), (mid_x_left, page_h - bottom_cut)); shape.finish(color=(1,0,0))
    shape.draw_line((mid_x_right, page_h - cur_br), (page_w, page_h - cur_br)); shape.finish(color=(1,0,0))
    shape.commit()
    st.image(page_guide.get_pixmap(dpi=int(150*zoom_level)).tobytes(), width=min(int(1000*zoom_level), 2000))

    # 저장 로직
    if start_save:
        if not os.path.exists(folder_name): os.makedirs(folder_name)
        uploaded_file.seek(0)
        doc_save = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        is_pdf_mode = "PDF" in save_format
        if is_pdf_mode: out_pdf = fitz.open()

        progress_bar = st.progress(0)
        q_cnt = 1
        final_idx = doc.page_count - 1 

        for i in range(doc_save.page_count):
            pg = doc_save.load_page(i)
            p_num = i + 1
            if p_num == 1: c_tl, c_tr = q1_top, q2_top 
            else: c_tl, c_tr = std_left_top, std_right_top
            c_br = last_bottom_cut if i == final_idx else bottom_cut

            rect_l = fitz.Rect(margin_left, c_tl, mid_x_left, pg.rect.height - bottom_cut)
            rect_r = fitz.Rect(mid_x_right, c_tr, pg.rect.width - margin_right, pg.rect.height - c_br)

            if is_pdf_mode:
                # PDF 모드
                if rect_l.width > 0:
                    out_pdf.insert_pdf(doc_save, from_page=i, to_page=i)
                    out_pdf[-1].set_cropbox(rect_l)
                if rect_r.width > 0:
                    out_pdf.insert_pdf(doc_save, from_page=i, to_page=i)
                    out_pdf[-1].set_cropbox(rect_r)
            else:
                # PNG 모드 (수정됨: 저장할 때마다 카운트 증가)
                # 1. 왼쪽 문제 저장
                if rect_l.width > 0:
                    pg.get_pixmap(clip=rect_l, dpi=200).save(f"{folder_name}/{q_cnt:02d}.png")
                    q_cnt += 1 # 저장했으므로 번호 증가
                
                # 2. 오른쪽 문제 저장
                if rect_r.width > 0:
                    pg.get_pixmap(clip=rect_r, dpi=200).save(f"{folder_name}/{q_cnt:02d}.png")
                    q_cnt += 1 # 저장했으므로 번호 증가

            progress_bar.progress((i+1)/doc_save.page_count)
        
        if is_pdf_mode:
            out_pdf.save(master_pdf_name)
            out_pdf.close()
            st.success(f"🎉 통합본 저장 완료: {master_pdf_name}")
        else:
            st.success(f"🎉 PNG 이미지 저장 완료! (총 {q_cnt-1}문제)")
        doc_save.close()