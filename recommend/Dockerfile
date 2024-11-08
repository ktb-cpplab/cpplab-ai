# 1. Python 베이스 이미지 설정
FROM python:3.12-slim as base

# 2. 필요한 빌드 의존성 및 pip 설치를 위한 빌드 스테이지
FROM base as builder

# 빌드용 의존성 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# pip 최신 버전 설치
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# 필요한 파일 복사 (의존성 파일만 먼저 복사하여 캐시 활용)
COPY requirements.txt ./

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 3. 실제 애플리케이션 파일을 복사하는 스테이지 (멀티 스테이지 빌드 사용)
FROM base

# 작업 디렉토리 설정
WORKDIR /app

# 빌드된 의존성 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 파일 복사
COPY recommend_course.py connect_ai_db.py embedding_text_vec.py ./

# 모델 파일이 큰 경우 필요 시 다운로드하거나 압축하여 배포
COPY models /app/models

# 애플리케이션 실행
CMD ["uvicorn", "recommend_course:app", "--host", "0.0.0.0", "--port", "5000"]
