FROM python:3.9

# 1. [핵심] 한글 깨짐 방지 & 인코딩 설정
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

# 2. 필수 시스템 패키지 (이미지 처리용 부품)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. 파일 복사
COPY . .

# 4. 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 포트 설정
EXPOSE 8080

# 6. 실행 (maker.py) - 파일 감시 끄기 포함
CMD ["streamlit", "run", "maker.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--browser.gatherUsageStats=false"]