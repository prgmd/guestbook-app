FROM python:3.11-slim
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/

# start.sh에 실행 권한 부여
RUN chmod +x /app/start.sh

# start.sh 스크립트로 컨테이너 실행
CMD ["/app/start.sh"]