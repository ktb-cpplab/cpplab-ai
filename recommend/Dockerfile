# 베이스 이미지로 Python 3.9 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 파일 복사
COPY recommend/requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY ./recommend /app/recommend

# config 디렉토리 생성 후, application.properties 복사 (Jenkins에서 시크릿 파일로 관리)
RUN mkdir -p /app/config
COPY application.properties /app/config/application.properties

# 환경 변수 설정 (필요 시)
# ENV APP_ENV=production

# 애플리케이션 포트 설정 (예: 8000 포트 사용 시)
EXPOSE 5000

# 애플리케이션 실행 명령어
# FastAPI를 사용한다면 uvicorn을 통해 실행 가능
CMD ["uvicorn", "recommend_course:app", "--host", "0.0.0.0", "--port", "8000"]
