# 1. Python 베이스 이미지 사용
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /code

# 3. 의존성 파일 복사 및 설치
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 4. 소스 코드 복사
COPY ./app /code/app

# 5. 서버 실행
# 0.0.0.0으로 호스트를 지정해야 도커 외부에서 접근 가능
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]