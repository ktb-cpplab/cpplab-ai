# 1. Python 베이스 이미지
FROM python:3.12-slim AS base

# 2. 빌드 의존성 및 필수 도구 설치 단계
FROM base AS builder

# 빌드용 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    make \
    automake \
    autoconf \
    libtool \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    curl \
    python3-pip \
    bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# pip 및 setuptools 업그레이드
RUN pip install --no-cache-dir --upgrade pip setuptools

# 작업 디렉토리 설정
WORKDIR /app

# S3에서 다운로드한 MeCab 사전 복사
COPY mecab /app/mecab

RUN chmod -R 755 /app/mecab

# 최신 config.guess 및 config.sub 다운로드
RUN cd /app/mecab && \
    curl -o ./config.guess https://git.savannah.gnu.org/cgit/config.git/plain/config.guess && \
    curl -o ./config.sub https://git.savannah.gnu.org/cgit/config.git/plain/config.sub && \
    chmod +x ./config.guess ./config.sub

# MeCab 설치
RUN cd /app/mecab && \
    find . -name "*.o" -delete && \
    find . -name "*.lo" -delete && \
    find . -name "*.la" -delete && \
    make clean || true && \
    bash ./configure && \
    make && \
    make install

RUN cd /app/mecab/mecab-ko-dic-2.1.1-20180720 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install

# mecab-python 빌드
RUN cd /app/mecab/mecab-ko-dic-2.1.1-20180720/mecab-0.996-ko-0.9.2/mecab-python-0.996 && \
    python3 setup.py build

# 필요한 파일만 먼저 복사하여 캐시 활용
COPY requirements.txt ./

# 의존성 설치 (uvicorn 포함)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install uvicorn

# 의존성 복사
# COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# # 실행 파일 복사
# COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

# 애플리케이션 파일 복사
COPY recommend_course.py connect_ai_db.py embedding_text_vec.py keywords.py tf_idf.py ./
COPY models /app/models

# 애플리케이션 실행
CMD ["uvicorn", "recommend_course:app", "--host", "0.0.0.0", "--port", "5000"]
