FROM python:3.11-slim
WORKDIR /app
COPY . .
# 백엔드와 동일한 라이브러리 설치
RUN pip install SQLAlchemy PyMySQL kafka-python
CMD ["python", "consumer.py"]