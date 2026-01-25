import streamlit as st
import omrlogic_drill as omrlogic
import pandas as pd
import json
import os
import re
import streamlit.components.v1 as components  # 이 줄을 import 쪽에 추가

# [데이터 파일 경로]
DATA_FILE = 'exam_data.json'

# --- 데이터 로드/저장 함수 ---
def load_data():
    """JSON 파일에서 수정사항/검토의견을 불러옵니다."""
    default_data = {
        "revisions": {
            "1회": "• 12번 문제: 선지 ④번 **'적절한'** -> **'적절하지 않은'**으로 수정",
            "2회": "• 5번 문제: **복수 정답 인정** (1번, 3번)"
        },
        "comments": {
            "1회": "• 난이도: **중상** (법률 지문 시간 배분 유의)",
            "2회": "• 난이도: **상** (논리퀴즈 다수 출제)"
        }
    }
    
    if not os.path.exists(DATA_FILE):
        return default_data
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_data

def save_data(data):
    """데이터를 JSON 파일에 저장합니다."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def format_text(text):
    """텍스트 포맷팅 (굵게, 줄바꿈)"""
    if not text: return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = text.replace("\n", "<br>")
    return text

# --- 데이터 불러오기 ---
exam_data = load_data()
REVISIONS_DB = exam_data['revisions']
COMMENTS_DB = exam_data['comments']

# --- 페이지 설정 ---
st.set_page_config(page_title="모바일 OMR", layout="centered")
# ==============================================================================
# [추가됨] 아이프레임 자동 높이 조절 스크립트
# ==============================================================================
def auto_resize_iframe():
    """
    Streamlit 앱의 높이를 계산하여 부모 창(아임웹)으로 메시지를 보냅니다.
    """
    js = """
    <script>
        function sendHeight() {
            // Streamlit 앱의 전체 높이를 계산 (약간의 여유값 +30)
            const height = window.parent.document.body.scrollHeight;
            
            // 아임웹(부모의 부모 창)으로 메시지 전송
            // 구조: Component Iframe -> Streamlit App -> Imweb
            window.parent.parent.postMessage({
                type: 'streamlit:height', 
                height: height 
            }, "*");
        }

        // 1. 처음 로드될 때 전송
        window.addEventListener('load', function() {
            setTimeout(sendHeight, 100); // 렌더링 시간 고려
        });

        // 2. 화면 크기가 변할 때마다 전송 (ResizeObserver)
        const observer = new ResizeObserver(entries => {
            sendHeight();
        });
        observer.observe(window.parent.document.body);
    </script>
    """
    # 높이 0짜리 숨겨진 iframe을 만들어 스크립트 실행
    components.html(js, height=0, width=0)

# 함수 실행 (이 코드가 있어야 작동합니다)
auto_resize_iframe()

# --- CSS 스타일 ---
st.markdown("""
<style>
    /* 1. 기본 리셋 */
    * { box-sizing: border-box !important; min-width: 0 !important; }
    .block-container { max-width: 450px !important; width: 100% !important; padding: 10px 5px !important; margin: 0 auto !important; }

    /* 2. 일반 버튼(st.button) 스타일 */
    .stButton > button {
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
        color: #666666 !important;
        font-weight: bold !important;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #f9f9f9 !important;
        border-color: #333333 !important;
        color: #333333 !important;
    }

    /* 3. Primary 버튼 (검정색) - 등록하기, 채점하기, 시험시작 */
    .stButton > button[kind="primary"] {
        background-color: #333333 !important;
        border: 2px solid #333333 !important;
        color: #ffffff !important;
        font-weight: bold !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #000000 !important;
        border-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* 4. 폼 버튼(잔재 처리) */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #333333 !important;
        border: 2px solid #333333 !important;
        color: #ffffff !important;
        width: 100%;
        margin-top: 5px !important;
    }

    /* 5. 기타 스타일 */
    .info-box { border: 1px solid #ddd !important; background-color: #f9f9f9 !important; border-radius: 5px !important; padding: 15px !important; margin-top: 2px !important; margin-bottom: 2px !important; color: #444 !important; font-size: 14px !important; line-height: 1.6 !important; }
    div[data-testid="stHorizontalBlock"] { flex-direction: row !important; gap: 0 !important; }
    div[data-testid="column"]:nth-of-type(1) { overflow: hidden !important; padding: 0 !important; display: flex; justify-content: center; align-items: center; }
    div[data-testid="column"]:nth-of-type(2) { width: auto !important; padding-left: 2px !important; display: flex; align-items: center; justify-content: center !important; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] { align-items: center !important; display: flex !important; flex-direction: column !important; width: 100% !important; }
    div[data-testid="column"]:nth-of-type(3) { width: auto !important; padding:0 !important; display: flex; align-items: center; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border: 2px solid #333 !important; border-radius: 0px !important; padding: 0 !important; width: 100% !important; background: linear-gradient(to right, #f0f2f6 0%, #f0f2f6 35px, #333 35px, #333 37px, #ffffff 37px, #ffffff 100%) !important; }
    div[role="radiogroup"] input[type="radio"], div[role="radiogroup"] label > div:first-child { display: none !important; }
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { border: 2px solid #ea5656 !important; border-radius: 50% !important; width: clamp(16px, 6vw, 24px) !important; height: clamp(22px, 8vw, 30px) !important; display: flex; justify-content: center; align-items: center; font-size: clamp(10px, 4vw, 13px) !important; font-weight: bold !important; color: #ea5656 !important; background: white !important; margin: 0 auto !important; }
    div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { background-color: black !important; border-color: black !important; color: black !important; }
    div[role="radiogroup"] { display: flex; justify-content: space-between; width: 100% !important; padding: 4px 0 !important; margin-top: -4px !important; max-width: 240px !important; margin: 0 auto !important; }
    div[role="radiogroup"] label { flex: 1; display: flex; justify-content: center; margin: 0 !important; padding: 0 !important; }
    div[data-testid="stForm"] { border: none !important; padding: 0 !important; width: 100% !important; }
    div[data-testid="stForm"] > div[data-testid="stVerticalBlock"] { gap: 0.3rem !important; }
    .q-num-box { font-weight: 800; text-align: center; color: #333; font-size: 13px; display: flex; align-items: center; justify-content: center; height: 30px; margin-top: 6px; }
    .header-box { font-weight: bold; text-align: center; color: #333; font-size: 13px; padding: 8px 0; white-space: nowrap; }
    .separator-line { position: relative; width: 100%; border-top: 1px dashed #bbb; height: 1px; margin-top: -8px !important; margin-bottom: -18px !important; z-index: 0; }
    .start-title { text-align: center; color: #333; margin-bottom: 20px; font-size: 28px !important; font-weight: 800; }
    .info-text { text-align: center; color: #666; font-size: 13px; line-height: 1.6; margin-top: 15px; margin-bottom: 5px; word-break: keep-all; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stAppDeployButton {display:none;} div[data-testid="stToolbar"] {display:none;}
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a { display: none !important; pointer-events: none !important; }
    hr { margin-top: 0px !important; margin-bottom: 20px !important; border-color: #e0e0e0 !important; }
    div[data-testid="InputInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 세션 초기화 ---
if 'exam_started' not in st.session_state: st.session_state['exam_started'] = False
if 'user_answers' not in st.session_state: st.session_state['user_answers'] = {}
if 'submitted' not in st.session_state: st.session_state['submitted'] = False
if 'show_revisions' not in st.session_state: st.session_state['show_revisions'] = False
if 'show_comments' not in st.session_state: st.session_state['show_comments'] = False
if 'page_view' not in st.session_state: st.session_state['page_view'] = 'main'
if 'temp_user_info' not in st.session_state: st.session_state['temp_user_info'] = {'num': '', 'name': ''}
if 'current_round' not in st.session_state: st.session_state['current_round'] = '1회' # 통계용 회차 저장

# ==============================================================================
# 로직 분기
# ==============================================================================

# ------------------------------------------------------------------------------
# [페이지 1] 질의 응답 및 관리자 페이지
# ------------------------------------------------------------------------------
if st.session_state['page_view'] == 'qna_list':
    u_num = st.session_state['temp_user_info']['num']
    u_name = st.session_state['temp_user_info']['name']
    is_admin = (u_num == '860111' and u_name == '신성우')

    h_col1, h_col2 = st.columns([8, 2], gap="small")
    with h_col1:
        st.markdown(f"### {'관리자 페이지' if is_admin else f'질의응답 ({u_name})'}")
    with h_col2:
        if st.button("⬅", use_container_width=True):
            st.session_state['page_view'] = 'main'
            st.rerun()

    if is_admin:
        tab_qna, tab_notice = st.tabs(["💬 질의응답 관리", "📢 공지사항 관리"])
        
        with tab_qna:
            all_qna = omrlogic.load_qna_data()
            my_list = all_qna[::-1]
            if not my_list:
                st.info("등록된 질문이 없습니다.")
            else:
                for idx, item in enumerate(my_list):
                    q_id = item['id']
                    status = "✅ 답변완료" if item['answer'] else "⏳ 답변대기"
                    title = f"[{item['round']} {item['q_num']}번] {status} - {item['u_name']}"
                    with st.expander(title):
                        st.markdown(f"**Q. {item['question']}**")
                        if item['answer']:
                            st.info(f"**A.** {item['answer']}")
                        st.markdown("---")
                        ans_input = st.text_area("답변 작성", value=item['answer'], key=f"ans_{q_id}")
                        if st.button("답변 등록", key=f"btn_{q_id}", type="primary"):
                            omrlogic.save_answer(q_id, ans_input)
                            st.success("답변이 저장되었습니다!")
                            st.rerun()

        with tab_notice:
            st.info("💡 내용에 **강조할 말** 처럼 별표 두 개를 쓰면 굵게 표시됩니다.")
            target_round = st.selectbox("편집할 회차 선택", [f"{i}회" for i in range(1, 9)])
            curr_rev = exam_data['revisions'].get(target_round, "")
            curr_cmt = exam_data['comments'].get(target_round, "")
            new_rev = st.text_area("📢 정오표(수정사항) 입력", value=curr_rev, height=100)
            new_cmt = st.text_area("💡 검토의견(총평) 입력", value=curr_cmt, height=100)
            if st.button("💾 내용 저장하기", type="primary"):
                exam_data['revisions'][target_round] = new_rev
                exam_data['comments'][target_round] = new_cmt
                save_data(exam_data)
                st.toast(f"{target_round} 내용이 저장되었습니다!", icon="✅")
                st.rerun()
    else:
        if st.button("✏️ 새 글 쓰기", type="primary", use_container_width=True):
            st.session_state['page_view'] = 'qna_write'
            st.rerun()
        st.divider()
        all_qna = omrlogic.load_qna_data()
        my_list = [q for q in all_qna if q['u_number'] == u_num][::-1]
        if not my_list:
            st.info("등록된 질문이 없습니다.")
        else:
            for idx, item in enumerate(my_list):
                status = "✅ 답변완료" if item['answer'] else "⏳ 답변대기"
                title = f"[{item['round']} {item['q_num']}번] {status} - {item['timestamp'][:10]}"
                with st.expander(title):
                    st.markdown(f"**Q. {item['question']}**")
                    if item['answer']:
                        st.success(f"**A.** {item['answer']}")
                        st.caption(f"답변일시: {item['ans_time']}")

# ------------------------------------------------------------------------------
# [페이지 2] 질의 응답 - 새 글 쓰기
# ------------------------------------------------------------------------------
elif st.session_state['page_view'] == 'qna_write':
    st.markdown("### ✏️ 질문 작성")
    q_round = st.selectbox("회차 선택", [f"{i}회" for i in range(1, 9)])
    q_num = st.number_input("문제 번호", min_value=1, max_value=40, step=1)
    q_content = st.text_area("질문 내용", height=150, placeholder="궁금한 내용을 자유롭게 적어주세요.")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, space, c2 = st.columns([6, 1.5, 1.5])
    with c1:
        submitted = st.button("등록하기", type="primary", use_container_width=True)
    with c2:
        cancelled = st.button("취소", use_container_width=True)
    if cancelled:
        st.session_state['page_view'] = 'qna_list'
        st.rerun()
    elif submitted:
        if not q_content:
            st.error("내용을 입력해주세요.")
        else:
            omrlogic.save_question(
                q_round, str(q_num), q_content, 
                st.session_state['temp_user_info']['num'], 
                st.session_state['temp_user_info']['name']
            )
            st.success("질문이 등록되었습니다.")
            st.session_state['page_view'] = 'qna_list'
            st.rerun()

# ------------------------------------------------------------------------------
# [페이지 3] 시험 통계 화면
# ------------------------------------------------------------------------------
elif st.session_state['page_view'] == 'stats':
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown("### 성적분포표 (임시)")
    with c2:
        if st.button("⬅", use_container_width=True):
            st.session_state['page_view'] = 'main'
            st.rerun()
    
    st.divider()

    curr_round_str = st.session_state.get('current_round', '1회')
    r_num = curr_round_str.replace("회", "")
    img1_path = f"data/{r_num}_1.jpg"
    img2_path = f"data/{r_num}_2.jpg"

    has_image = False
    
    if os.path.exists(img1_path):
        st.image(img1_path, use_container_width=True)
        has_image = True
    
    if os.path.exists(img2_path):
        st.image(img2_path, use_container_width=True)
        has_image = True

    if not has_image:
        # [수정된 부분] 회차 정보를 앞에 붙여서 출력
        st.info(f"{curr_round_str} 통계 이미지를 업데이트 중입니다.")

# ------------------------------------------------------------------------------
# [페이지 4] 메인 화면
# ------------------------------------------------------------------------------
else:
    if not st.session_state['exam_started']:
        st.markdown("<h1 class='start-title'>26년 신성우 모의고사<br>모바일 OMR</h1>", unsafe_allow_html=True)
        
        with st.container(border=True):
            round_options = [f"{i}회" for i in range(1, 9)]
            selected_round = st.selectbox("회차", round_options)
            
            # DB 데이터 불러오기
            rev_content = exam_data['revisions'].get(selected_round, "")
            cmt_content = exam_data['comments'].get(selected_round, "")

            if st.button("수정사항 보기", use_container_width=True):
                st.session_state['show_revisions'] = not st.session_state['show_revisions']
            if st.session_state['show_revisions']:
                if not rev_content.strip():
                    display_rev = "등록된 수정사항이 없습니다."
                else:
                    display_rev = format_text(rev_content)
                st.markdown(f'<div class="info-box"><strong style="display:block; margin-bottom:8px; color:#d63031;">📢 [{selected_round} 정오표]</strong>{display_rev}</div>', unsafe_allow_html=True)

            if st.button("검토의견 보기", use_container_width=True):
                st.session_state['show_comments'] = not st.session_state['show_comments']
            if st.session_state['show_comments']:
                if not cmt_content.strip():
                    display_cmt = "등록된 검토의견이 없습니다."
                else:
                    display_cmt = format_text(cmt_content)
                st.markdown(f'<div class="info-box"><strong style="display:block; margin-bottom:8px; color:#0984e3;">💡 [{selected_round} 검토의견]</strong>{display_cmt}</div>', unsafe_allow_html=True)

            st.divider()
            
            # ------------------------------------------------------------------
            # [수정된 부분] 라벨 숨김(label_visibility="collapsed") + Placeholder 변경
            # ------------------------------------------------------------------
            user_number = st.text_input("수험번호", placeholder="수험번호를 입력하세요", key="input_num", label_visibility="collapsed")
            user_name = st.text_input("성명", placeholder="성명을 입력하세요", key="input_name", label_visibility="collapsed")
            
            start_btn_clicked = st.button("시험 시작", type="primary", use_container_width=True)
            warning_msg_box = st.empty() 

            if start_btn_clicked:
                if not user_name or not user_number:
                    warning_msg_box.warning("수험번호와 성명을 먼저 입력해주세요.")
                elif not user_number.isdigit():
                    warning_msg_box.error("🚨 수험번호는 숫자만 입력 가능합니다.")
                else:
                    st.session_state.update({
                        'info_type': "모의고사", 
                        'info_subject': "신성우", 
                        'info_year': selected_round, 
                        'info_number': user_number, 
                        'info_name': user_name,
                        'exam_started': True, 
                        'user_answers': {}, 
                        'submitted': False
                    })
                    st.rerun()
            st.markdown("<div class='info-text'>수정사항, 검토의견, 통계 업로드 중입니다.<br>(1.27. 완료예정)<br><br> 입력한 수험번호와 성명을 기억해야 <br> 맞춤형 통계와 질의 응답을 확인할 수 있습니다.</div>", unsafe_allow_html=True)

            c1, space, c2 = st.columns([1, 0.05, 1]) 
            with c1:
                if st.button("시험 통계 보기", use_container_width=True): 
                    st.session_state['current_round'] = selected_round 
                    st.session_state['page_view'] = 'stats'            
                    st.rerun()
            with c2:
                if st.button("질의 응답", use_container_width=True):
                    if not user_number or not user_name:
                        warning_msg_box.warning("수험번호와 성명을 먼저 입력해주세요.")
                    else:
                        st.session_state['temp_user_info'] = {'num': user_number, 'name': user_name}
                        st.session_state['page_view'] = 'qna_list'
                        st.rerun()

    # 결과 화면
    elif st.session_state['submitted']:
        e_subj = st.session_state['info_subject']
        u_round = st.session_state['info_year']
        u_name = st.session_state['info_name']
        correct_answers = omrlogic.get_answer_key(st.session_state['info_type'], e_subj, u_round)
        score, wrong_details = omrlogic.grade_exam(st.session_state['user_answers'], correct_answers)

        st.markdown(f"<h2 style='text-align:center;'>📄 채점 결과</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; font-size:14px; color:#666;'>{u_round} | {u_name}님</div>", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<h1 style='text-align:center; font-size: 50px; color:#333; margin:0;'>{score:.1f}<span style='font-size:20px;'>점</span></h1>", unsafe_allow_html=True)
        if score == 100:
            st.success("🎉 축하합니다! 만점입니다!")
        else:
            st.info(f"총 {len(correct_answers)}문제 중 {len(wrong_details)}개 틀렸습니다.")
            st.markdown("### ❌ 오답 내역")
            for item in wrong_details:
                q_n = item['q_num']
                u_a = item['user_ans']
                c_a = item['correct_ans']
                st.markdown(f"<div style='background-color:#fff5f5; border:1px solid #ffcccc; padding:10px; border-radius:5px; margin-bottom:8px;'><b>Q{q_n}.</b> &nbsp; 내 답: <span style='color:red; font-weight:bold;'>{u_a}</span> &nbsp;|&nbsp; 정답: <span style='color:blue; font-weight:bold;'>{c_a}</span></div>", unsafe_allow_html=True)
        st.divider()
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("다시 풀기", use_container_width=True): 
                st.session_state['user_answers'] = {}; st.session_state['submitted'] = False; st.rerun()
        with c2:
            if st.button("홈으로", use_container_width=True): 
                st.session_state['exam_started'] = False; st.rerun()

    # OMR 작성 화면
    else:
        st.markdown("""<style>.block-container { max-width: 300px !important; }</style>""", unsafe_allow_html=True)
        e_subj = st.session_state['info_subject']
        u_name = st.session_state['info_name']
        u_round = st.session_state['info_year']
        h_col1, h_col2 = st.columns([7.5, 2.5]) 
        with h_col1: st.markdown(f"<div style='padding-top:5px;'><b>{u_round}</b> | {u_name}</div>", unsafe_allow_html=True)
        with h_col2: 
            if st.button("⬅", key="back_omr", use_container_width=True): st.session_state['exam_started'] = False; st.rerun()

        correct_answers = omrlogic.get_answer_key(st.session_state['info_type'], e_subj, u_round)
        total_q = len(correct_answers)

        if total_q > 0:
            with st.form("omr_form", border=False):
                with st.container(border=True):
                    h1, h2 = st.columns([2.5, 7.5]) 
                    with h1: st.markdown("<div class='header-box'>문번</div>", unsafe_allow_html=True)
                    with h2: st.markdown("<div class='header-box'>답 란&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>", unsafe_allow_html=True)
                    st.markdown("<div style='border-top: 2px solid #333; width:100%; line-height:0;'>&nbsp;</div>", unsafe_allow_html=True)
                    for q in range(1, total_q + 1):
                        if q > 1 and (q - 1) % 5 == 0: st.markdown("<div class='separator-line'></div>", unsafe_allow_html=True)
                        r1, r2 = st.columns([2.5, 7.5])
                        with r1: st.markdown(f"<div class='q-num-box'>{q}</div>", unsafe_allow_html=True)
                        with r2:
                            val = st.radio(f"q_{q}", [1,2,3,4,5], horizontal=True, label_visibility="collapsed", key=f"q_{q}", index=None)
                            st.session_state['user_answers'][q] = val
                if st.form_submit_button("채점하기", type="primary", use_container_width=True):
                    c_answers = omrlogic.get_answer_key(st.session_state['info_type'], e_subj, u_round)
                    score, _ = omrlogic.grade_exam(st.session_state['user_answers'], c_answers)
                    omrlogic.save_exam_result(st.session_state['info_name'], st.session_state['info_number'], u_round, score, st.session_state['user_answers'])
                    st.session_state['submitted'] = True
                    st.rerun()
        else:
            st.error(f"'{u_round}'에 대한 정답 데이터가 없습니다.")
            if st.button("돌아가기"): st.session_state['exam_started'] = False; st.rerun()