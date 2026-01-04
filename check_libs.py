import streamlit as st

st.title("범인 색출 테스트")

st.write("1. Streamlit 로딩 성공")

try:
    import fitz  # PyMuPDF
    st.write(f"2. PyMuPDF(fitz) 로딩 성공! 버전: {fitz.__doc__}")
except Exception as e:
    st.error(f"❌ PyMuPDF 로딩 실패: {e}")

try:
    from PIL import Image
    st.write("3. Pillow(이미지) 로딩 성공!")
except Exception as e:
    st.error(f"❌ Pillow 로딩 실패: {e}")

st.success("모든 라이브러리가 정상입니다! 이제 maker.py를 올려도 됩니다.")