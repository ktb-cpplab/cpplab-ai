# 1. Python 베이스 이미지
FROM python:3.12-slim AS base

# 2. 빌드 의존성 및 필수 도구 설치 단계
FROM base AS builder

# 빌드용 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일만 먼저 복사하여 캐시 활용
COPY requirements.txt ./

# 의존성 설치 (여기에 uvicorn 설치 명령어 추가)
RUN pip install --no-cache-dir -r requirements.txt && pip install uvicorn

# 3. 최종 이미지 설정
FROM base

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# 실행 파일 복사
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

# 애플리케이션 파일 복사
COPY recommend_course.py connect_ai_db.py embedding_text_vec.py keywords.py tf_idf.py ./
COPY models /app/models
COPY mecab /app/mecab

RUN 
# 애플리케이션 실행
CMD ["uvicorn", "recommend_course:app", "--host", "0.0.0.0", "--port", "5000"]
