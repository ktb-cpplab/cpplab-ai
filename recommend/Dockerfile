# 1. Python 베이스 이미지
FROM python:3.12-slim as base

# 빌드 의존성 및 필수 도구 설치 단계
FROM base as builder

# 빌드용 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일만 먼저 복사하여 캐시 활용
COPY requirements.txt ./

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 2. 최종 이미지 설정
FROM base

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 및 애플리케이션 파일 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY recommend_course.py connect_ai_db.py embedding_text_vec.py ./

# 모델 파일 복사
COPY models /app/models

# 애플리케이션 실행
CMD ["uvicorn", "recommend_course:app", "--host", "0.0.0.0", "--port", "5000"]
