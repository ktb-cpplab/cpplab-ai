# Python 베이스 이미지
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# PostgreSQL의 pg_config 설치와 함께 pip 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc curl && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 필요한 파일 복사
COPY recommend_course.py connect_ai_db.py embedding_text_vec.py requirements.txt ./

# 모델 파일이 큰 경우 필요 시 다운로드하거나 압축하여 배포
COPY models /app/models

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 실행
CMD ["uvicorn", "recommend_course:app", "--host", "0.0.0.0", "--port", "5000"]