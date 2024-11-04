# 베이스 이미지 선택
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY recommend_course.py /app/
COPY connect_ai_db.py /app/
COPY embedding_text_vec.py /app/
COPY requirements.txt /app/
COPY models /app/models  

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 모델 경로 환경 변수 설정
ENV MODEL_PATH=/app/models

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "recommend_course:app", "--host", "0.0.0.0", "--port", "5000"]