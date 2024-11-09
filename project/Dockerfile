# project 관련 Dockerfile
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# PostgreSQL의 pg_config 설치를 위해 필요한 라이브러리 추가
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# 필요한 파일 복사
COPY main.py /app/
COPY requirements.txt /app/
COPY models /app/models
COPY services /app/services

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
