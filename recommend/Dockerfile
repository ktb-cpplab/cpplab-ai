# 1. Python 베이스 이미지
FROM python:3.12-slim AS base

# 2. 빌드 의존성 및 필수 도구 설치 단계
FROM base AS builder

# 빌드용 패키지 및 MeCab 설치에 필요한 라이브러리 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    mecab libmecab-dev mecab-ipadic-utf8 build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일만 먼저 복사하여 캐시 활용
COPY requirements.txt ./

# Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt && pip install uvicorn

# S3에서 다운로드한 MeCab 사전 복사
COPY mecab /app/mecab

# 12. MeCab 사전 빌드
RUN cd /app/mecab/mecab-ko-dic-2.1.1-20180720 && \
    chmod +x ./configure && \
    ./configure && \
    make && \
    make install

# 3. 최종 이미지 설정
FROM base

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

# 애플리케이션 파일 복사
COPY recommend_course.py connect_ai_db.py embedding_text_vec.py keywords.py tf_idf.py ./
COPY models /app/models

# MeCab 사전 권한 설정 (필요한 경우)
RUN chmod -R 755 /app/mecab/mecab-ko-dic-2.1.1-20180720

# 애플리케이션 실행
CMD ["uvicorn", "recommend_course:app", "--host", "0.0.0.0", "--port", "5000"]