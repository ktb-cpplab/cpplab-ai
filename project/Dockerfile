# project 관련 Dockerfile
FROM python:3.8

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY main.py /app/
COPY requirements.txt /app/
# 루트 디렉토리의 .env 파일을 복사
COPY ../.env /app/.env  

# 의존성 설치
RUN pip install -r requirements.txt

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]